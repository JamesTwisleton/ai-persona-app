"use client";

import React, { useState, FormEvent } from "react";

type QueryBoxProps = {
  onSearch: (query: string) => void;
};

export default function QueryBox({ onSearch }: QueryBoxProps) {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <form
      onSubmit={(e: FormEvent) => {
        e.preventDefault();
        onSearch(searchQuery);
      }}
      className="flex items-center w-full max-w-lg mx-auto"
    >
      {/* Container for input and clear button */}
      <div className="flex items-center flex-grow border border-gray-300 rounded-l-full bg-white focus-within:ring-2 focus-within:ring-blue-500">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Ask a question to get an instant opinion..."
          className="flex-grow p-3 rounded-l-full focus:outline-none text-black bg-white"
        />
        {searchQuery && (
          <button
            type="button"
            onClick={() => setSearchQuery("")}
            className="px-3 text-black hover:bg-gray-200 transition duration-300  rounded-l-full rounded-r-full"
          >
            ×
          </button>
        )}
      </div>

      <button
        type="submit"
        className="p-3 rounded-r-full bg-blue-500 hover:bg-blue-700 transition duration-300"
      >
        {/* TODO: replace this with an icon */}
        <span dangerouslySetInnerHTML={{ __html: "&#128269;" }} />
      </button>
    </form>
  );
}
