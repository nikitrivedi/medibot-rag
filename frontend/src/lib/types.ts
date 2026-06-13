export type Source =
  | {
      type: "document";
      source_document: string;
      section_title: string | string[];
      collection: string;
      rerank_score: number;
      text: string;
    }
  | {
      type: "sql";
      sql: string;
      results: string;
    };

export type ChatResponse = {
  answer: string;
  retrieval_type: string;
  role: string;
  sources: Source[];
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  role: string;
  username: string;
};

export type Session = LoginResponse;

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  retrieval_type?: string;
  sources?: Source[];
};
