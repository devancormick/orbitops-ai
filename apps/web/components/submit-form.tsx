"use client";

import { useState } from "react";

import { createFile, submitRun } from "../lib/api";
import { workflows } from "../lib/data";

export function SubmitForm() {
  const [message, setMessage] = useState<string>("");
  const [pending, setPending] = useState(false);

  async function handleSubmit(formData: FormData) {
    setPending(true);
    setMessage("");

        const workflow = workflows.find((item) => item.name === formData.get("workflow_name")) ?? workflows[0];
        const filename = String(formData.get("filename") || "").trim();
        const fileIds: string[] = [];
        if (filename) {
          const upload = await createFile({
            filename,
            content_type: "application/pdf",
            workspace: String(formData.get("workspace"))
          });
          if (upload.ok) {
            fileIds.push(upload.file.id);
          }
        }
        const result = await submitRun({
          workflow_name: String(formData.get("workflow_name")),
          task_type: workflow.taskType,
          latency_target: String(formData.get("latency_target")),
          requires_review: formData.get("requires_review") === "on",
          context: String(formData.get("context")),
          workspace: String(formData.get("workspace")),
          uploaded_file_ids: fileIds
        });

    setPending(false);
    if (!result.ok) {
      setMessage("Unable to queue run right now.");
      return;
    }

    setMessage(`Queued ${result.run.workflow} as ${result.run.id}.`);
  }

  return (
    <form
      className="card form-card"
      action={async (formData) => {
        await handleSubmit(formData);
      }}
    >
      <label className="field">
        <span>Workspace</span>
        <input name="workspace" defaultValue="Operations Workspace" />
      </label>
      <label className="field">
        <span>Workflow template</span>
        <select name="workflow_name" defaultValue={workflows[0].name}>
          {workflows.map((workflow) => (
            <option key={workflow.name} value={workflow.name}>
              {workflow.name}
            </option>
          ))}
        </select>
      </label>
      <label className="field">
        <span>Latency target</span>
        <select name="latency_target" defaultValue="balanced">
          <option value="fast">Fast</option>
          <option value="balanced">Balanced</option>
          <option value="thorough">Thorough</option>
        </select>
      </label>
      <label className="field">
        <span>Request context</span>
        <textarea
          name="context"
          rows={6}
          defaultValue="Upload updated vendor registration documents and extract ownership, sanctions, and onboarding notes."
        />
      </label>
      <label className="field">
        <span>Source file name</span>
        <input name="filename" defaultValue="vendor-registration-update.pdf" />
      </label>
      <label className="checkbox-row">
        <input name="requires_review" type="checkbox" defaultChecked />
        <span>Require human review before finalizing</span>
      </label>
      <div className="action-row">
        <button className="button button-primary" type="submit" disabled={pending}>
          {pending ? "Queueing..." : "Queue run"}
        </button>
        <button className="button button-secondary" type="button">Save draft</button>
      </div>
      {message ? <p className="status-note">{message}</p> : null}
    </form>
  );
}
