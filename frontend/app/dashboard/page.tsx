
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ThemeSwitcher } from "@/components/theme-switcher";
import { api, token } from "@/lib/api";

type Doc = {
  id: number;
  filename: string;
  file_type: string;
  detected_language: string;
};

type Job = {
  id: number;
  document_id: number;
  analysis_type: string;
  status: string;
  progress: number;
};

type SimilarityMatch = {
  source_filename?: string;
  source_chunk?: number;
  matched_chunk?: number;
  score?: number;
  method?: string;
  source_excerpt?: string;
  matched_excerpt?: string;
};

// Convert technical values into readable text
function readableValue(value: any): string {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Not available";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (value === "not_calibrated") {
    return "Not calibrated";
  }

  if (value === "requires_dataset_validation") {
    return "Requires dataset validation";
  }

  if (value === "EXPLORATORY_SIGNALS_ONLY") {
    return "Inconclusive - exploratory signals only";
  }

  if (value === "en") {
    return "English";
  }

  return String(value);
}

// Safely read nested report fields
function getReportValue(
  data: any,
  path: string
): any {
  return path
    .split(".")
    .reduce(
      (current, key) => current?.[key],
      data
    );
}

// Convert 0.639 into 63.9%
function formatPercentage(value: any): string {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Not available";
  }

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "Not available";
  }

  const percentage =
    number >= 0 && number <= 1
      ? number * 100
      : number;

  return `${percentage.toFixed(1)}%`;
}

// Generate a human-readable CSV report
function downloadCSV(
  data: any,
  filename: string,
  documentName: string,
  jobId: number
) {
  const report = data || {};

  const rawMatches = getReportValue(
    report,
    "semantic.matches"
  );

  const matches: SimilarityMatch[] =
    Array.isArray(rawMatches)
      ? rawMatches
      : [];

  const matchCount = matches.length;

  const classification = getReportValue(
    report,
    "ai_content.classification"
  );

  const aiAssessment =
    classification === "EXPLORATORY_SIGNALS_ONLY"
      ? "Inconclusive - exploratory signals only"
      : readableValue(classification);

  const aiScore = readableValue(
    getReportValue(
      report,
      "ai_content.score"
    )
  );

  const confidence = readableValue(
    getReportValue(
      report,
      "ai_content.confidence"
    )
  );

  const detectedLanguage = readableValue(
    getReportValue(
      report,
      "detected_language"
    )
  );

  const similarityStatus = readableValue(
    getReportValue(
      report,
      "semantic.language_evaluation.evaluation_status"
    )
  );

  // Main report rows
  const rows: string[][] = [
    ["VERILEX AI - ANALYSIS REPORT", ""],
    ["Report ID", String(jobId)],
    ["Document Name", documentName],
    ["Report Generated", new Date().toLocaleString()],
    ["Analysis Status", "Completed"],
    [
      "Analysis Type",
      readableValue(
        getReportValue(
          report,
          "analysis_type"
        )
      ),
    ],
    ["Detected Language", detectedLanguage],

    ["", ""],
    ["DOCUMENT INFORMATION", ""],

    [
      "Total Characters",
      readableValue(
        getReportValue(
          report,
          "document_intelligence.characters"
        )
      ),
    ],

    [
      "Document Contains Text",
      readableValue(
        getReportValue(
          report,
          "document_intelligence.nonempty"
        )
      ),
    ],

    [
      "Document Ready for Analysis",
      readableValue(
        getReportValue(
          report,
          "document_intelligence.ready"
        )
      ),
    ],

    [
      "Text Sections Analyzed",
      readableValue(
        getReportValue(
          report,
          "semantic.chunks_analyzed"
        )
      ),
    ],

    ["", ""],
    ["SIMILARITY ANALYSIS", ""],

    [
      "Similarity Matches Found",
      String(matchCount),
    ],

    [
      "Highest Similarity",
      formatPercentage(
        getReportValue(
          report,
          "semantic.top_similarity"
        )
      ),
    ],

    [
      "Similarity Evaluation",
      similarityStatus,
    ],

    ["", ""],
  ];

  // Add individual similarity evidence
  rows.push([
    "INDIVIDUAL SIMILARITY MATCH DETAILS",
    "",
  ]);

  if (matches.length > 0) {
    matches.forEach((match, index) => {
      rows.push(
        ["", ""],
        [
          "Match Number",
          `Match #${index + 1}`,
        ],
        [
          "Source Document",
          readableValue(
            match.source_filename
          ),
        ],
        [
          "Individual Similarity",
          formatPercentage(
            match.score
          ),
        ],
        [
          "Uploaded Document Section",
          readableValue(
            match.source_chunk
          ),
        ],
        [
          "Source Document Section",
          readableValue(
            match.matched_chunk
          ),
        ],
        [
          "Original Text Excerpt",
          readableValue(
            match.source_excerpt
          ),
        ],
        [
          "Matched Source Excerpt",
          readableValue(
            match.matched_excerpt
          ),
        ],
        [
          "Comparison Method",
          readableValue(
            match.method
          ),
        ]
      );
    });
  } else {
    rows.push([
      "Match Details",
      "No individual similarity matches are available in the saved report.",
    ]);
  }

  // AI writing analysis
  rows.push(
    ["", ""],
    ["AI WRITING ANALYSIS", ""],

    [
      "AI Writing Assessment",
      aiAssessment,
    ],

    [
      "AI Detection Score",
      aiScore,
    ],

    [
      "Detection Confidence",
      confidence,
    ],

    [
      "Lexical Diversity",
      readableValue(
        getReportValue(
          report,
          "ai_content.signals.lexical_diversity"
        )
      ),
    ],

    [
      "Word Entropy",
      readableValue(
        getReportValue(
          report,
          "ai_content.signals.word_entropy_bits"
        )
      ),
    ],

    [
      "Average Words per Sentence",
      readableValue(
        getReportValue(
          report,
          "ai_content.signals.average_sentence_words"
        )
      ),
    ],

    [
      "Repetition Indicator",
      formatPercentage(
        getReportValue(
          report,
          "ai_content.signals.repetition_ratio"
        )
      ),
    ],

    [
      "AI Analysis Warning",
      readableValue(
        getReportValue(
          report,
          "ai_content.warning"
        )
      ),
    ],

    ["", ""],
    ["REPORT VALIDATION", ""],

    [
      "Analysis Method Available",
      readableValue(
        getReportValue(
          report,
          "report_validation.method_present"
        )
      ),
    ],

    [
      "Evidence Count",
      readableValue(
        getReportValue(
          report,
          "report_validation.evidence_count"
        )
      ),
    ],

    ["", ""],
    ["ANALYSIS INTERPRETATION", ""],

    [
      "System Interpretation",
      readableValue(
        getReportValue(
          report,
          "interpretation"
        )
      ),
    ],

    [
      "Important Disclaimer",
      "AI-writing indicators are not proof of authorship. Similarity results require human review.",
    ]
  );

  // Escape CSV values and prevent spreadsheet formula execution
  const escapeCSV = (value: any): string => {
    let text = String(value ?? "");

    if (/^[=+\-@\t\r]/.test(text)) {
      text = "'" + text;
    }

    return `"${text.replace(/"/g, '""')}"`;
  };

  const csv = rows
    .map((row) =>
      row.map(escapeCSV).join(",")
    )
    .join("\r\n");

  const blob = new Blob(
    ["\uFEFF" + csv],
    {
      type: "text/csv;charset=utf-8;",
    }
  );

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = filename;

  document.body.appendChild(link);
  link.click();
  link.remove();

  window.setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 1000);
}

export default function Dashboard() {
  const router = useRouter();

  const [docs, D] = useState<Doc[]>([]);
  const [jobs, J] = useState<Job[]>([]);
  const [file, F] = useState<File | null>(null);
  const [busy, B] = useState(false);
  const [msg, M] = useState("");
  const [err, E] = useState("");

  // Refresh documents and analysis history
  async function refresh() {
    const [documents, analyses] = await Promise.all([
      api("/documents"),
      api("/analysis"),
    ]);

    D(documents);
    J(analyses);
  }

  // Check authentication
  useEffect(() => {
    if (!token()) {
      router.replace("/login");
      return;
    }

    refresh().catch((error) => {
      E(
        error instanceof Error
          ? error.message
          : "Unable to load dashboard"
      );
    });
  }, [router]);

  // Upload document
  async function upload() {
    if (!file) return;

    B(true);
    E("");
    M("");

    try {
      const form = new FormData();
      form.append("file", file);

      const result = await api(
        "/documents/upload",
        {
          method: "POST",
          body: form,
        }
      );

      M(
        `Uploaded ${result.filename}; extracted ${result.characters_extracted} characters.`
      );

      F(null);

      await refresh();
    } catch (error) {
      E(
        error instanceof Error
          ? error.message
          : "Upload failed"
      );
    } finally {
      B(false);
    }
  }

  // Start document analysis
  async function analyze(id: number) {
    B(true);
    E("");
    M("");

    try {
      await api(
        "/analysis/submit",
        {
          method: "POST",
          body: JSON.stringify({
            document_id: id,
            analysis_type: "complete",
          }),
        }
      );

      M(
        "Analysis queued. Refresh to view its status."
      );

      await refresh();
    } catch (error) {
      E(
        error instanceof Error
          ? error.message
          : "Analysis failed"
      );
    } finally {
      B(false);
    }
  }

  // Delete document
  async function remove(id: number) {
    E("");
    M("");

    try {
      await api(
        `/documents/${id}`,
        {
          method: "DELETE",
        }
      );

      M("Document deleted successfully.");

      await refresh();
    } catch (error) {
      E(
        error instanceof Error
          ? error.message
          : "Delete failed"
      );
    }
  }

  // Download detailed CSV report
  async function exportReport(id: number) {
    E("");
    M("");

    try {
      const report = await api(
        `/analysis/${id}/report`
      );

      if (
        report.result === null ||
        report.result === undefined
      ) {
        throw new Error(
          "No report data is available for this analysis."
        );
      }

      const job = jobs.find(
        (item) => item.id === id
      );

      const document = docs.find(
        (item) =>
          item.id === job?.document_id
      );

      const documentName =
        document?.filename ||
        `Document-${job?.document_id ?? "unknown"}`;

      downloadCSV(
        report.result,
        `VeriLex-Report-${id}.csv`,
        documentName,
        id
      );

      const matches = getReportValue(
        report.result,
        "semantic.matches"
      );

      const count = Array.isArray(matches)
        ? matches.length
        : 0;

      M(
        `CSV report downloaded. Individual matches included: ${count}.`
      );
    } catch (error) {
      E(
        error instanceof Error
          ? error.message
          : "CSV download failed"
      );
    }
  }

  // Sign out
  function logout() {
    localStorage.removeItem("verilex-token");
    router.push("/");
  }

  return (
    <div className="shell">
      <header className="top">
        <Link
          className="brand"
          href="/"
        >
          VeriLex AI
        </Link>

        <div className="actions">
          <ThemeSwitcher />

          <button
            className="btn"
            onClick={logout}
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="dashboard">
        <aside className="sidebar">
          <a className="side active">
            Overview
          </a>

          <a
            className="side"
            href="#upload"
          >
            New analysis
          </a>

          <a
            className="side"
            href="#docs"
          >
            Documents
          </a>

          <a
            className="side"
            href="#history"
          >
            History
          </a>
        </aside>

        <main className="main">
          <div className="eyebrow">
            Private workspace
          </div>

          <h1>Analysis overview</h1>

          <p className="muted">
            Upload documents and inspect real analysis evidence.
          </p>

          {/* Dashboard statistics */}
          <div className="stats">
            <div className="stat">
              <span>Documents</span>
              <strong>{docs.length}</strong>
            </div>

            <div className="stat">
              <span>Jobs</span>
              <strong>{jobs.length}</strong>
            </div>

            <div className="stat">
              <span>Completed</span>
              <strong>
                {
                  jobs.filter(
                    (job) =>
                      job.status === "COMPLETED"
                  ).length
                }
              </strong>
            </div>

            <div className="stat">
              <span>Pending</span>
              <strong>
                {
                  jobs.filter((job) =>
                    ["QUEUED", "PROCESSING"].includes(
                      job.status
                    )
                  ).length
                }
              </strong>
            </div>
          </div>

          {/* Success message */}
          {msg && (
            <div className="notice">
              {msg}
            </div>
          )}

          {/* Error message */}
          {err && (
            <div className="notice error">
              {err}
            </div>
          )}

          {/* Upload Section */}
          <section
            className="panel"
            id="upload"
          >
            <h2>Upload a document</h2>

            <div className="drop">
              <p>
                PDF · DOCX · TXT · Python · Java ·
                JavaScript · TypeScript · C/C++ · PHP
              </p>

              <p className="muted">
                Maximum 20 MB
              </p>

              <input
                type="file"
                accept=".pdf,.docx,.txt,.py,.java,.js,.jsx,.ts,.tsx,.c,.cpp,.h,.hpp,.php"
                onChange={(event) =>
                  F(
                    event.target.files?.[0] || null
                  )
                }
              />

              <p>{file?.name}</p>

              <button
                className="btn primary"
                disabled={!file || busy}
                onClick={upload}
              >
                {busy
                  ? "Please wait..."
                  : "Upload securely"}
              </button>
            </div>
          </section>

          {/* Document Library */}
          <section
            className="panel"
            id="docs"
          >
            <h2>Document library</h2>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Type</th>
                    <th>Language</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {docs.map((document) => (
                    <tr key={document.id}>
                      <td>{document.filename}</td>

                      <td>{document.file_type}</td>

                      <td>
                        {document.detected_language}
                      </td>

                      <td>
                        <button
                          className="btn primary"
                          disabled={busy}
                          onClick={() =>
                            analyze(document.id)
                          }
                        >
                          Analyze
                        </button>

                        {" "}

                        <button
                          className="btn"
                          disabled={busy}
                          onClick={() =>
                            remove(document.id)
                          }
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}

                  {!docs.length && (
                    <tr>
                      <td
                        colSpan={4}
                        className="muted"
                      >
                        No documents uploaded yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Analysis History */}
          <section
            className="panel"
            id="history"
          >
            <h2>Analysis history</h2>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Job</th>
                    <th>Document</th>
                    <th>Status</th>
                    <th>Progress</th>
                    <th>Report</th>
                  </tr>
                </thead>

                <tbody>
                  {jobs.map((job) => {
                    const document = docs.find(
                      (item) =>
                        item.id === job.document_id
                    );

                    return (
                      <tr key={job.id}>
                        <td>#{job.id}</td>

                        <td>
                          {document?.filename ||
                            `Document #${job.document_id}`}
                        </td>

                        <td>{job.status}</td>

                        <td>{job.progress}%</td>

                        <td>
                          {job.status === "COMPLETED" ? (
                            <button
                              className="btn primary"
                              onClick={() =>
                                exportReport(job.id)
                              }
                            >
                              Download CSV
                            </button>
                          ) : (
                            "—"
                          )}
                        </td>
                      </tr>
                    );
                  })}

                  {!jobs.length && (
                    <tr>
                      <td
                        colSpan={5}
                        className="muted"
                      >
                        No analysis jobs yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="notice">
              Similarity is a human-review signal, not proof
              of plagiarism. AI-writing indicators are not
              authorship evidence.
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
