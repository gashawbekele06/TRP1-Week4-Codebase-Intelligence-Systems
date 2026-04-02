export interface GraphNode {
  id: string;
  node_type?: string;
  path?: string;
  language?: string;
  purpose_statement?: string;
  domain_cluster?: string;
  is_dead_code_candidate?: boolean;
  change_velocity_30d?: number;
  name?: string;
  storage_type?: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  edge_type?: string;
  weight?: number;
}

export interface RawGraph {
  nodes: GraphNode[];
  edges?: GraphEdge[];
  links?: GraphEdge[];
  directed?: boolean;
}

export interface ModulePurpose {
  path: string;
  language?: string;
  purpose_statement: string;
  docstring?: string;
  documentation_drift: boolean;
  documentation_drift_reason?: string;
  inferred_domain?: string;
}

export interface DomainBoundary {
  domain: string;
  module_count: number;
  representative_modules?: string[];
}

export interface FDEAnswers {
  q1_primary_ingestion_path: string;
  q2_critical_outputs: string;
  q3_blast_radius: string;
  q4_logic_concentration: string;
  q5_git_velocity_map: string;
}

export interface SemanticReport {
  module_purpose_statements: ModulePurpose[];
  business_domain_boundaries: DomainBoundary[];
  five_fde_day_one_answers: FDEAnswers;
  warnings: string[];
  model_policy?: { bulk_extraction_model: string; synthesis_model: string };
}

export interface TraceEntry {
  timestamp_utc: string;
  agent: string;
  action: string;
  confidence: number;
  analysis_method: string;
  evidence_sources: { file: string; line_range: string; method: string }[];
  metadata?: Record<string, unknown>;
}

export interface CartographyData {
  moduleGraph: RawGraph | null;
  lineageGraph: { graph?: RawGraph } | null;
  lineageMeta: { sources: string[]; sinks: string[] };
  semanticReport: SemanticReport | null;
  codebaseMd: string | null;
  onboardingBrief: string | null;
  traceLog: TraceEntry[];
}
