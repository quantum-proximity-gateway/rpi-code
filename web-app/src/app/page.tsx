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
    // const response = await fetch("http://localhost:8000/api/devices");
    // const data = await response.json();
    // return data;

    // Placeholder data
    const data: User[] = [
      { name: "Alice", distance: 0, loggedIn: false },
      { name: "Bob", distance: Math.random()*10, loggedIn: true },
      { name: "Charlie", distance: Math.random()*10, loggedIn: false },
      { name: "Dale", distance: Math.random()*10, loggedIn: false },
    ];
    // Simulate API response delay
    return new Promise(resolve => setTimeout(() => resolve(data), 100));
  }

  useEffect(() => {
    // Call API every half second to update the user data
    const interval = setInterval(() => {
      getUserData().then(data => setUsers(data));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  const calculateCircleSize = (distance: number) => {
    const minSize = 50;
    const maxSize = 350;
        
    const size = minSize + (maxSize - minSize) / distance;
    return Math.min(Math.max(size, minSize), maxSize);
  }

  return (
    <div style={{display: "flex", flexDirection: "row", justifyContent: "center", alignItems: "center", flexWrap: "wrap", height: "100vh", gap: "50px", padding: "50px"}}>
      {users.map(user => {
        const circleSize = calculateCircleSize(user.distance);

        return (
          <div style={{display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: "5px"}}>
            <p>{user.name}</p>
            <div key={user.name} style={{display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", width: `${circleSize}px`, height: `${circleSize}px`, border:`3px solid ${user.loggedIn ? "blue" : user.distance < 3 ? "green" : "red"}`, borderRadius: "50%", overflow: "hidden", whiteSpace: "nowrap" ,transition: "width 0.5s, height 0.5s, border-color 0.5s"}}>
              <p>{user.distance.toFixed(2)}m</p>
              {user.loggedIn && <p>Logged In</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
