"use client";

import { useEffect, useState } from "react";

import { Alert } from "@/components/ui";
import { api } from "@/lib/api";
import type { PhotoSearchResult } from "@/lib/types";

export function PhotoSearch({
  open,
  onClose,
  onResults,
}: {
  open: boolean;
  onClose: () => void;
  onResults: (result: PhotoSearchResult, filename: string) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [hint, setHint] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  useEffect(() => {
    if (open) return;
    setFile(null);
    setPreview("");
    setHint("");
    setError("");
  }, [open]);

  function choose(next: File | null) {
    setError("");
    setFile(next);
    setPreview(next ? URL.createObjectURL(next) : "");
  }

  function close() {
    choose(null);
    setHint("");
    setError("");
    onClose();
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const form = new FormData();
      form.append("file", file);
      if (hint.trim()) form.append("hint", hint.trim());
      const result = await api<PhotoSearchResult>("/catalogue/image-search", {
        method: "POST",
        body: form,
        auth: false,
      });
      onResults(result, file.name);
      close();
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (!open) return null;

  return (
    <section className="card card-pad" style={{ marginBottom: 18 }}>
      <div className="spread" style={{ alignItems: "flex-start" }}>
        <div>
          <strong style={{ fontSize: ".95rem" }}>Search by photo</strong>
          <p className="small faint" style={{ marginTop: 4 }}>
            Upload a product photo. The demo reads keywords from the file name and your hint.
          </p>
        </div>
        <button type="button" className="btn btn-ghost btn-sm" onClick={close} disabled={busy}>
          Close
        </button>
      </div>
      <form onSubmit={submit} style={{ marginTop: 14 }}>
        <div className="row" style={{ gap: 14, flexWrap: "wrap", alignItems: "flex-end" }}>
          <label className="field" style={{ minWidth: 220 }}>
            <span>Photo</span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              onChange={(event) => choose(event.target.files?.[0] ?? null)}
            />
          </label>
          <label className="field" style={{ flex: "1 1 260px" }}>
            <span>What is in the photo? (optional)</span>
            <input
              value={hint}
              onChange={(event) => setHint(event.target.value)}
              placeholder="e.g. kettle, wrap dress, body butter"
              maxLength={120}
            />
          </label>
          <button type="submit" className="btn btn-primary" disabled={!file || busy}>
            {busy ? "Matching…" : "Find products"}
          </button>
        </div>
        {preview ? (
          <img
            src={preview}
            alt="Selected photo preview"
            style={{
              width: 96,
              height: 96,
              objectFit: "cover",
              borderRadius: 10,
              marginTop: 14,
              border: "1px solid var(--line)",
            }}
          />
        ) : null}
        {error ? (
          <div style={{ marginTop: 12 }}>
            <Alert kind="error">{error}</Alert>
          </div>
        ) : null}
      </form>
    </section>
  );
}
