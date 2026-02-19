"use client";

import { useState } from "react";

import { downloadDocument, generateDocument, sendDocumentEmail, startIntake } from "../lib/api";
import { templates } from "../lib/data";

export function SubmitForm() {
  const [selectedTemplateKey, setSelectedTemplateKey] = useState(templates[0].template_key);
  const [message, setMessage] = useState("Start the guided intake, capture the contract fields, and generate a ready-to-review agreement.");
  const [pending, setPending] = useState(false);
  const [generatedId, setGeneratedId] = useState<string | null>(null);
  const [preview, setPreview] = useState<{ title: string; summary: string } | null>(null);

  const selectedTemplate = templates.find((item) => item.template_key === selectedTemplateKey) ?? templates[0];

  return (
    <form
      className="card form-card"
      onSubmit={async (event) => {
        event.preventDefault();
        setPending(true);
        setMessage("");
        const formData = new FormData(event.currentTarget);

        const basePayload = {
          template_key: String(formData.get("template_key")),
          workspace: String(formData.get("workspace")),
          agent_name: String(formData.get("agent_name")),
          client_email: String(formData.get("client_email")),
          notes: String(formData.get("notes"))
        };

        const intake = await startIntake(basePayload);
        if (!intake.ok) {
          setPending(false);
          setMessage("Unable to start the guided intake.");
          return;
        }

        const responses = Object.fromEntries(
          selectedTemplate.fields.map((field) => [field.key, String(formData.get(field.key) || "").trim()])
        );

        const result = await generateDocument({ ...basePayload, responses });
        setPending(false);
        if (!result.ok) {
          setMessage("Unable to generate the agreement right now.");
          return;
        }

        setGeneratedId(result.document.id);
        setPreview({ title: result.document.preview_title, summary: result.document.summary });
        setMessage(`Generated ${result.document.template_name} as ${result.document.id}.`);
      }}
    >
      <label className="field">
        <span>Contract template</span>
        <select
          name="template_key"
          value={selectedTemplateKey}
          onChange={(event) => setSelectedTemplateKey(event.target.value)}
        >
          {templates.map((template) => (
            <option key={template.template_key} value={template.template_key}>
              {template.name}
            </option>
          ))}
        </select>
      </label>
      <label className="field">
        <span>Agent name</span>
        <input name="agent_name" defaultValue="Devan Cormick" />
      </label>
      <label className="field">
        <span>Client email</span>
        <input name="client_email" defaultValue="agent@sunlinerealty.com" />
      </label>
      <label className="field">
        <span>Workspace</span>
        <input name="workspace" defaultValue="Sunline Realty" />
      </label>
      {selectedTemplate.fields.map((field, index) => (
        <label className="field" key={field.key}>
          <span>{index + 1}. {field.label}</span>
          <input name={field.key} placeholder={field.question} />
        </label>
      ))}
      <label className="field">
        <span>Agent notes</span>
        <textarea
          name="notes"
          rows={4}
          defaultValue="Use the guided intake flow to collect any missing deal details before final delivery."
        />
      </label>
      <div className="action-row">
        <button className="button button-primary" type="submit" disabled={pending}>
          {pending ? "Generating..." : "Generate agreement"}
        </button>
        <button
          className="button button-secondary"
          type="button"
          disabled={!generatedId}
          onClick={async () => {
            if (!generatedId) {
              return;
            }
            const email = String(formDataValue("client_email"));
            const result = await sendDocumentEmail(generatedId, email);
            setMessage(result.ok ? `Simulated email delivery for ${generatedId}.` : "Unable to email the agreement.");
          }}
        >
          Email PDF
        </button>
        <button
          className="button button-secondary"
          type="button"
          disabled={!generatedId}
          onClick={async () => {
            if (!generatedId) {
              return;
            }
            const result = await downloadDocument(generatedId);
            setMessage(result.ok ? `Simulated download for ${generatedId}.` : "Unable to download the agreement.");
          }}
        >
          Download PDF
        </button>
      </div>
      {preview ? (
        <div className="preview-panel">
          <strong>{preview.title}</strong>
          <p>{preview.summary}</p>
        </div>
      ) : null}
      <p className="status-note">{message}</p>
    </form>
  );
}

function formDataValue(name: string): string {
  const field = document.querySelector(`input[name="${name}"]`) as HTMLInputElement | null;
  return field?.value ?? "";
}
