import { render } from "@testing-library/react";
import Root from "./root.component";

jest.mock(
  "@mui/material",
  () => ({
    __esModule: true,
    Box: ({ children }) => <div>{children}</div>,
    Stack: ({ children }) => <div>{children}</div>,
    Paper: ({ children }) => <div>{children}</div>,
    List: ({ children }) => <ul>{children}</ul>,
    ListItem: ({ children }) => <li>{children}</li>,
    TextField: (props) => <input {...props} />,
    IconButton: ({ children, ...props }) => <button {...props}>{children}</button>,
  }),
  { virtual: true }
);

jest.mock("@mui/icons-material/Send", () => () => <span>SendIcon</span>, {
  virtual: true,
});

describe("Root component", () => {
  it("renders chat input", () => {
    const { getByPlaceholderText } = render(<Root />);
    expect(getByPlaceholderText(/Type your message/i)).toBeInTheDocument();
  });
});
