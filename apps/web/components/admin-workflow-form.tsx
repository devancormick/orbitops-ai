"use client";

import { useState } from "react";

import { createWorkflow } from "../lib/api";

export function AdminWorkflowForm() {
  const [message, setMessage] = useState("Create workflow templates that become immediately available to operators.");
  const [pending, setPending] = useState(false);

  return (
    <form
      className="card form-card"
      onSubmit={async (event) => {
        event.preventDefault();
        setPending(true);
        const formData = new FormData(event.currentTarget);
        const result = await createWorkflow({
          name: String(formData.get("name")),
          task_type: String(formData.get("task_type")),
          primary_model: String(formData.get("primary_model")),
          fallback_model: String(formData.get("fallback_model")),
          review_required: formData.get("review_required") === "on",
          workspace: String(formData.get("workspace"))
        });
        setPending(false);
        setMessage(result.ok ? `Created workflow ${result.workflow.name}.` : "Unable to create workflow.");
      }}
    >
      <label className="field">
        <span>Name</span>
        <input name="name" defaultValue="Invoice Exception Review" />
      </label>
      <label className="field">
        <span>Task type</span>
        <select name="task_type" defaultValue="classify">
          <option value="summarize">Summarize</option>
          <option value="extract">Extract</option>
          <option value="classify">Classify</option>
          <option value="compare">Compare</option>
          <option value="draft">Draft</option>
        </select>
      </label>
      <label className="field">
        <span>Primary model</span>
        <input name="primary_model" defaultValue="gpt-4.1-mini" />
      </label>
      <label className="field">
        <span>Fallback model</span>
        <input name="fallback_model" defaultValue="claude-3-5-sonnet" />
      </label>
      <label className="field">
        <span>Workspace</span>
        <input name="workspace" defaultValue="Finance Ops" />
      </label>
      <label className="checkbox-row">
        <input name="review_required" type="checkbox" />
        <span>Require review</span>
      </label>
      <div className="action-row">
        <button className="button button-primary" type="submit" disabled={pending}>
          {pending ? "Saving..." : "Create workflow"}
        </button>
      </div>
      <p className="status-note">{message}</p>
    </form>
  );
}
