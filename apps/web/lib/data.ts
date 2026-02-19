export type ContractField = {
  key: string;
  label: string;
  question: string;
  required: boolean;
};

export type ContractTemplate = {
  id?: number;
  name: string;
  template_key: string;
  description: string;
  agreement_type: "listing_agreement" | "purchase_sale_agreement";
  review_required: boolean;
  workspace: string;
  active: boolean;
  fields: ContractField[];
};

export type GeneratedDocument = {
  id: string;
  template_name: string;
  template_key: string;
  agreement_type: string;
  workspace: string;
  status: "draft" | "pending_review" | "ready" | "emailed" | "downloaded";
  generated_at: string;
  requested_by: string;
  recipient_email: string;
  preview_title: string;
  summary: string;
  field_values: Record<string, string>;
  preview_markdown: string;
  email_status: string;
  download_status: string;
};

export type ReviewItem = {
  id: string;
  template_name: string;
  summary: string;
  reviewer: string;
  priority: "high" | "medium";
  status: "open" | "approved" | "rerun_requested";
  requested_by: string;
};

export const templates: ContractTemplate[] = [
  {
    name: "Listing Agreement",
    template_key: "listing-agreement",
    description: "Capture seller details, listing dates, price, and commission terms for a ready-to-review listing packet.",
    agreement_type: "listing_agreement",
    review_required: true,
    workspace: "Sunline Realty",
    active: true,
    fields: [
      { key: "property_address", label: "Property address", question: "What property address is being listed?", required: true },
      { key: "seller_name", label: "Seller name", question: "Who is the seller or owner?", required: true },
      { key: "listing_price", label: "Listing price", question: "What listing price should appear in the contract?", required: true },
      { key: "listing_start_date", label: "Listing start date", question: "When should the listing begin?", required: true },
      { key: "listing_end_date", label: "Listing end date", question: "When should the listing expire?", required: true },
      { key: "commission_rate", label: "Commission rate", question: "What commission rate applies?", required: true }
    ]
  },
  {
    name: "Purchase & Sale Agreement",
    template_key: "purchase-sale-agreement",
    description: "Collect buyer, seller, price, earnest money, and closing terms through a guided AI-style intake flow.",
    agreement_type: "purchase_sale_agreement",
    review_required: true,
    workspace: "Sunline Realty",
    active: true,
    fields: [
      { key: "property_address", label: "Property address", question: "What property address should appear on the agreement?", required: true },
      { key: "buyer_name", label: "Buyer name", question: "Who is the buyer?", required: true },
      { key: "seller_name", label: "Seller name", question: "Who is the seller?", required: true },
      { key: "purchase_price", label: "Purchase price", question: "What is the agreed purchase price?", required: true },
      { key: "closing_date", label: "Closing date", question: "What is the closing date?", required: true },
      { key: "earnest_money", label: "Earnest money", question: "How much earnest money should be included?", required: true }
    ]
  }
];

export const documentHistory: GeneratedDocument[] = [
  {
    id: "DOC-4021",
    template_name: "Listing Agreement",
    template_key: "listing-agreement",
    agreement_type: "listing_agreement",
    workspace: "Sunline Realty",
    status: "pending_review",
    generated_at: "09:12 AM",
    requested_by: "D. Cormick",
    recipient_email: "agent@sunlinerealty.com",
    preview_title: "Listing Agreement for 414 Maple Ridge Drive",
    summary: "Listing packet generated and waiting for broker review before delivery.",
    field_values: {
      property_address: "414 Maple Ridge Drive, Nashville, TN",
      seller_name: "Claire Hudson",
      listing_price: "$685,000",
      listing_start_date: "2026-02-24",
      listing_end_date: "2026-08-24",
      commission_rate: "5.5%"
    },
    preview_markdown: "# Listing Agreement\n\n- Property Address: 414 Maple Ridge Drive, Nashville, TN",
    email_status: "not_sent",
    download_status: "ready"
  }
];

export const reviewQueue: ReviewItem[] = [
  {
    id: "DOC-4021",
    template_name: "Listing Agreement",
    summary: "Commission and listing dates should be confirmed before release.",
    reviewer: "Broker Review",
    priority: "high",
    status: "open",
    requested_by: "D. Cormick"
  }
];
