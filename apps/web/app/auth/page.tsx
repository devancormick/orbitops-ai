import { AuthForm } from "../../components/auth-form";
import { Navigation } from "../../components/nav";

export default function AuthPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Authentication</p>
          <h1 className="page-title">Sign in to launch intake sessions, generate agreements, and manage templates.</h1>
        </section>
        <AuthForm />
      </main>
    </>
  );
}
