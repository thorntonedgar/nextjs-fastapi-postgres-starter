"use client"; // Mark as Client Component

import { useEffect, useState } from "react";

// Types for User and Message
type User = {
  id: string;
  name: string;
};

type Message = {
  id: number;
  user_id: number;
  content: string;
  is_bot: boolean;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  const [user, setUser] = useState<User | null>(null); // User state
  const [messages, setMessages] = useState<Message[]>([]); // Messages state
  const [newMessage, setNewMessage] = useState<string>(""); // Input message
  const [error, setError] = useState<string | null>(null); // Error state

  // Polling interval (in milliseconds)
  const POLLING_INTERVAL = 3000;

  // Fetch the current user information on component mount
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch(`${apiUrl}/users/me`);
        const data = await response.json();
        setUser(data);
      } catch (err) {
        setError("Error fetching user information");
      }
    };

    fetchUser();
  }, []);

  // Fetch messages from the API
  const fetchMessages = async () => {
    try {
      const response = await fetch(`${apiUrl}/threads/1/messages`);
      const data = await response.json();
      setMessages(data);
    } catch (err) {
      setError("Error fetching messages");
    }
  };

  // Poll for new messages at regular intervals
  useEffect(() => {
    fetchMessages(); // Initial fetch
    const intervalId = setInterval(fetchMessages, POLLING_INTERVAL); // Poll every 3 seconds

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, []);

  // Handle message input change
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNewMessage(event.target.value);
  };

  // Handle sending the message
  const handleSendMessage = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!newMessage.trim()) return; // Do not send empty messages

    const messageData = {
      thread_id: 1, // Assuming thread 1
      user_id: parseInt(user?.id ?? "1"), // Get user_id from the state
      content: newMessage,
    };

    try {
      const response = await fetch(`${apiUrl}/messages/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(messageData),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      // Clear the input after sending the message
      setNewMessage("");
      // Refresh the messages list
      fetchMessages();

    } catch (err) {
      setError("Error sending message");
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      {error && <p className="text-red-500">{error}</p>}
      {user && <h1>Hello, {user.name}!</h1>}
      
      <div className="w-full max-w-lg">
        <h2 className="text-xl mb-4">Messages:</h2>
        {messages.length === 0 ? (
          <p>No messages found.</p>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`p-3 my-2 rounded ${message.is_bot ? "bg-gray-100" : "bg-blue-200"}`}
            >
              <p><strong>{message.is_bot ? "Bot" : `User ${message.user_id}`}:</strong> {message.content}</p>
            </div>
          ))
        )}
      </div>

      {/* Message form */}
      <form onSubmit={handleSendMessage} className="mt-6 w-full max-w-lg flex">
        <input
          type="text"
          value={newMessage}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className="flex-grow p-2 border rounded mr-2"
        />
        <button
          type="submit"
          className="p-2 bg-blue-500 text-white rounded"
          disabled={!newMessage.trim()} // Disable button if input is empty
        >
          Send
        </button>
      </form>
    </main>
  );
}
