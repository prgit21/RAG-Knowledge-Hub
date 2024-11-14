export default function Root(props) {
  return (
    <section>
      {props.name} is mounted!
      <br />
      <a href="/react">On angular shell, react is mounted</a>
      <br />
      <a href="/dashboard">Go To Angular App</a>
    </section>
  );
}
