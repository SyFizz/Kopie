import { BookOpen } from 'lucide-react'

function App() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
      <section className="text-center space-y-4">
        <BookOpen
          aria-hidden="true"
          size={48}
          className="mx-auto text-[hsl(var(--primary))]"
        />
        <h1 className="text-3xl font-semibold">Kopie — Évaluation</h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          Scaffold opérationnel. Story 1.1 — placeholder.
        </p>
      </section>
    </main>
  )
}

export default App
