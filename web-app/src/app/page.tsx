'use client';
import { useEffect, useState } from "react";

/*
  Website to showcase distances to each user, continuously need to call the API to get the latest data.
  Each user is a circle on a plain background, growing in size as the distance to the user decreases.
  The user's name is displayed on the circle.
  If the distance is less than 3m, the circle should be green.
  If the user is logged in (detected by camera), the circle should say "Logged in", and be blue.
*/

export default function Home() {

  type User = {
    name: string;
    distance: number;
    loggedIn: boolean;
  }

  const [users, setUsers] = useState<User[]>([]);

  async function getUserData(): Promise<User[]> {
    // const response = await fetch("http://localhost:8000/api/users");
    // const data = await response.json();
    // return data;

    // Placeholder data
    const data: User[] = [
      { name: "Alice", distance: 2.5, loggedIn: false },
      { name: "Bob", distance: 4.0, loggedIn: true },
      { name: "Charlie", distance: 1.0, loggedIn: false },
      { name: "Dale", distance: 0.5, loggedIn: true },
    ];
    // Simulate API response delay
    return new Promise(resolve => setTimeout(() => resolve(data), 100));
  }

  useEffect(() => {
    const interval = setInterval(() => {
      getUserData().then(data => setUsers(data));
    }, 500); // Calling the API every half second to update the user data

    return () => clearInterval(interval);
  }, []);


  return (
    <div>
      {users.map(user => (
        <div key={user.name}>
          <p>Name: {user.name}</p>
          <p>Distance: {user.distance}</p>
          <p>Logged In: {user.loggedIn ? "Yes" : "No"}</p>
        </div>
      ))}
    </div>
  );
}
