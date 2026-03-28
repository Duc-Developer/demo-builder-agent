import React from "react";
import AppLayout from "./components/AppLayout.jsx";
import TodoPage from "./pages/TodoPage.jsx";

export default function App() {
  return (
    <AppLayout>
      <TodoPage />
    </AppLayout>
  );
}

