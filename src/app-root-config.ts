import {
  navigateToUrl,
  pathToActiveWhen,
  registerApplication,
  start,
} from "single-spa";
import {
  constructApplications,
  constructRoutes,
  constructLayoutEngine,
} from "single-spa-layout";
import microfrontendLayout from "./microfrontend-layout.html";

const PROTECTED_APPLICATIONS = new Set([
  "@react-app/react-app",
  "dashboard-app",
]);

function hasAuthToken(): boolean {
  if (typeof document !== "undefined") {
    const match = document.cookie.match(/(?:^|; )authToken=([^;]+)/);
    if (match && match[1]) {
      return true;
    }
  }

  if (typeof window !== "undefined" && window.localStorage) {
    try {
      return Boolean(window.localStorage.getItem("authToken"));
    } catch (error) {
      console.warn("Unable to access auth token from localStorage.", error);
    }
  }

  return false;
}

function ensureAuthenticated(): boolean {
  if (hasAuthToken()) {
    return true;
  }

  if (typeof window !== "undefined" && window.location.pathname !== "/") {
    navigateToUrl("/");
  }

  return false;
}

function toActivityFn(activity: any): (location: Location) => boolean {
  if (typeof activity === "function") {
    return activity;
  }

  if (Array.isArray(activity)) {
    const fns = activity.map((item) => toActivityFn(item));
    return (location: Location) => fns.some((fn) => fn(location));
  }

  return pathToActiveWhen(activity);
}

const routes = constructRoutes(microfrontendLayout);
const applications = constructApplications({
  routes,
  loadApp({ name }) {
    return System.import(name);
  },
});

applications.forEach((application) => {
  if (!PROTECTED_APPLICATIONS.has(application.name)) {
    return;
  }

  const originalActiveWhen = toActivityFn(application.activeWhen);
  application.activeWhen = (location) => {
    if (!originalActiveWhen(location)) {
      return false;
    }

    return ensureAuthenticated();
  };
});

const layoutEngine = constructLayoutEngine({ routes, applications });

applications.forEach(registerApplication);
layoutEngine.activate();
start();
