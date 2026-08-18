import React, { useEffect, useState } from "react";
import { ApiClient } from "../api/client";
import { ActiveProfile } from "../api/types";
import { useConnection } from "../state/connection";
import "./ProfileStatus.css";

export const ProfileStatus: React.FC = () => {
  const { state } = useConnection();
  const [profile, setProfile] = useState<ActiveProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    if (state.apiHealth === "nominal") {
      ApiClient.getActiveProfile()
        .then(p => {
          if (mounted) {
            setProfile(p);
            setError(null);
          }
        })
        .catch(e => {
          if (mounted) setError(e.message);
        });
    } else {
      setProfile(null);
    }
    return () => {
      mounted = false;
    };
  }, [state.apiHealth]);

  return (
    <div className="profile-panel">
      <h2>Profile</h2>
      <hr />
      {state.apiHealth !== "nominal" ? (
        <div className="status-pending">Waiting for API connection...</div>
      ) : error ? (
        <div className="error-msg">Failed to load profile: {error}</div>
      ) : profile ? (
        <ul>
          <li><strong>Name:</strong> {profile.name}</li>
          <li><strong>Version:</strong> {profile.version}</li>
          <li><strong>Description:</strong> {profile.description}</li>
        </ul>
      ) : (
        <div className="status-pending">Loading profile...</div>
      )}
    </div>
  );
};
