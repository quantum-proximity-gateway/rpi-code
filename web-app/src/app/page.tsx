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
  const [online, setOnline] = useState<boolean>(true);

  async function getUserData(): Promise<User[]> {
    try {
      const response = await fetch("http://localhost:5000/api/devices");
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setOnline(true);
      return data;
    } catch (error) {
      console.error("Failed to fetch user data:", error);
      setOnline(false);
      return [];
    }
  }

  useEffect(() => {
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
    online ? (
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
    ): (
      <div style={{display: "flex", justifyContent: "center", alignItems: "center", height: "100vh"}}>
        <p>Offline: Unable to fetch user data</p>
      </div>
    )
  );
}
