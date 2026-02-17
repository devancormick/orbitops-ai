import { AuthForm } from "../../components/auth-form";
import { Navigation } from "../../components/nav";

export default function AuthPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Authentication</p>
          <h1 className="page-title">Sign in to create runs, upload files, and manage workflows.</h1>
        </section>
        <AuthForm />
      </main>
    </>
  );
}
