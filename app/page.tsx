import Chat from "@/components/Chat";

export default function HomePage() {
  return (
    <main className="mx-auto flex h-screen max-w-5xl flex-col px-4 py-4">
      <header className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">sabi_synth · data chat</h1>
          <p className="text-sm text-gray-400">
            Ask about Portuguese SME financials — the agent answers with charts,
            tables, and numbers.
          </p>
        </div>
      </header>
      <Chat />
    </main>
  );
}
