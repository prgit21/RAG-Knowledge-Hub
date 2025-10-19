import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
  HttpParams,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { navigateToUrl } from 'single-spa';
import { AppConfigService } from './app-config.service';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor(
    private http: HttpClient,
    private appConfig: AppConfigService
  ) {}

  private get apiUrl(): string {
    return this.appConfig.getApiUrl();
  }

  private getAuthToken(): string | null {
    if (typeof document !== 'undefined') {
      const match = document.cookie.match(/(?:^|; )authToken=([^;]+)/);
      if (match) {
        return decodeURIComponent(match[1]);
      }
    }
    try {
      return localStorage.getItem('authToken');
    } catch (error) {
      console.warn('Unable to read auth token from localStorage.', error);
    }
    return null;
  }

  private clearAuthState(): void {
    if (typeof document !== 'undefined') {
      document.cookie = 'authToken=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
    try {
      localStorage.removeItem('authToken');
    } catch (error) {
      console.warn('Unable to clear auth token from localStorage.', error);
    }
  }

  private getAuthHeaders(): HttpHeaders {
    const token = this.getAuthToken();
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }

  private getAuthOptions() {
    return {
      headers: this.getAuthHeaders(),
      withCredentials: true,
    };
  }

  private handleError(error: HttpErrorResponse) {
    if (error.status === 401) {
      this.clearAuthState();
      navigateToUrl('/');
    }
    return throwError(() => error);
  }

  getHelloMessage(): Observable<any> {
    return this.http
      .get<any>(`${this.apiUrl}/hello`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  getProtectedData(): Observable<any> {
    return this.http
      .get<any>(`${this.apiUrl}/protected`, this.getAuthOptions())
      .pipe(catchError((error) => this.handleError(error)));
  }

  postLogin(username: string, password: string): Observable<any> {
    const body = new HttpParams()
      .set('username', username)
      .set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http.post(`${this.apiUrl}/login`, body.toString(), {
      headers,
      withCredentials: true,
    });
  }

}
