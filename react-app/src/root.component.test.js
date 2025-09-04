import { render } from "@testing-library/react";
import Root from "./root.component";

describe("Root component", () => {
  it("renders chat input", () => {
    const { getByPlaceholderText } = render(<Root />);
    expect(getByPlaceholderText(/Type your message/i)).toBeInTheDocument();
  });
});
