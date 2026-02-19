"use client";

import { useState } from "react";

import { createTemplate } from "../lib/api";

export function AdminWorkflowForm() {
  const [message, setMessage] = useState("Create private contract templates that become immediately available to agents.");
  const [pending, setPending] = useState(false);

  return (
    <form
      className="card form-card"
      onSubmit={async (event) => {
        event.preventDefault();
        setPending(true);
        const formData = new FormData(event.currentTarget);
        const result = await createTemplate({
          name: String(formData.get("name")),
          template_key: String(formData.get("template_key")),
          description: String(formData.get("description")),
          agreement_type: String(formData.get("agreement_type")) as "listing_agreement" | "purchase_sale_agreement",
          review_required: formData.get("review_required") === "on",
          workspace: String(formData.get("workspace")),
          fields: [
            {
              key: "property_address",
              label: "Property address",
              question: "What property address should appear on this template?",
              required: true
            }
          ]
        });
        setPending(false);
        setMessage(result.ok ? `Created template ${result.template.name}.` : "Unable to create template.");
      }}
    >
      <label className="field">
        <span>Name</span>
        <input name="name" defaultValue="Listing Agreement" />
      </label>
      <label className="field">
        <span>Template key</span>
        <input name="template_key" defaultValue="listing-agreement" />
      </label>
      <label className="field">
        <span>Description</span>
        <textarea
          name="description"
          rows={4}
          defaultValue="Guided listing contract flow for seller details, pricing, dates, and commission terms."
        />
      </label>
      <label className="field">
        <span>Agreement type</span>
        <select name="agreement_type" defaultValue="listing_agreement">
          <option value="listing_agreement">Listing Agreement</option>
          <option value="purchase_sale_agreement">Purchase &amp; Sale Agreement</option>
        </select>
      </label>
      <label className="field">
        <span>Workspace</span>
        <input name="workspace" defaultValue="Sunline Realty" />
      </label>
      <label className="checkbox-row">
        <input name="review_required" type="checkbox" defaultChecked />
        <span>Require broker review before delivery</span>
      </label>
      <div className="action-row">
        <button className="button button-primary" type="submit" disabled={pending}>
          {pending ? "Saving..." : "Create template"}
        </button>
      </div>
      <p className="status-note">{message}</p>
    </form>
  );
}
