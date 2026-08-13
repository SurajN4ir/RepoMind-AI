/**
 * features/landing/hooks/use-mock-demo.ts
 *
 * State machine hook for the live mock demo section.
 *
 * Models the full query lifecycle:
 * IDLE → TYPING → PLANNING → SEARCHING → BUILDING → ANSWERING → DONE
 *
 * No backend integration. All responses are scripted mock data.
 */

"use client";

import { useCallback, useEffect, useReducer, useRef } from "react";

// ---------------------------------------------------------------------------
// State machine
// ---------------------------------------------------------------------------

export type DemoPhase =
  | "idle"
  | "typing"
  | "planning"
  | "searching"
  | "building"
  | "answering"
  | "done";

export interface DemoState {
  phase: DemoPhase;
  query: string;
  displayedQuery: string;
  answer: string;
  displayedAnswer: string;
  searchResults: string[];
  contextFiles: string[];
}

type DemoAction =
  | { type: "START"; query: string }
  | { type: "TYPE_CHAR"; char: string }
  | { type: "ADVANCE_PHASE"; phase: DemoPhase }
  | { type: "ADD_RESULT"; result: string }
  | { type: "ADD_CONTEXT"; file: string }
  | { type: "TYPE_ANSWER_CHAR"; char: string }
  | { type: "RESET" };

const initialState: DemoState = {
  phase: "idle",
  query: "",
  displayedQuery: "",
  answer: "",
  displayedAnswer: "",
  searchResults: [],
  contextFiles: [],
};

function reducer(state: DemoState, action: DemoAction): DemoState {
  switch (action.type) {
    case "START":
      return { ...initialState, query: action.query, phase: "typing" };
    case "TYPE_CHAR":
      return { ...state, displayedQuery: state.displayedQuery + action.char };
    case "ADVANCE_PHASE":
      return { ...state, phase: action.phase };
    case "ADD_RESULT":
      return { ...state, searchResults: [...state.searchResults, action.result] };
    case "ADD_CONTEXT":
      return { ...state, contextFiles: [...state.contextFiles, action.file] };
    case "TYPE_ANSWER_CHAR":
      return { ...state, displayedAnswer: state.displayedAnswer + action.char };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const MOCK_RESULTS: Record<string, { results: string[]; context: string[]; answer: string }> = {
  default: {
    results: [
      "src/auth/jwt_handler.py · JWTHandler.create_token()",
      "src/auth/middleware.py · AuthMiddleware.__call__()",
      "src/auth/schemas.py · TokenPayload",
      "src/api/dependencies.py · get_current_user()",
      "src/auth/password.py · verify_password()",
    ],
    context: [
      "src/auth/jwt_handler.py",
      "src/auth/middleware.py",
      "src/api/dependencies.py",
    ],
    answer: `Authentication in RepoMind uses **JWT tokens** issued by \`JWTHandler.create_token()\`.

When a request arrives, \`AuthMiddleware\` intercepts it and calls \`get_current_user()\` from \`dependencies.py\`, which:

1. Extracts the Bearer token from the Authorization header
2. Decodes it using the shared secret via \`JWTHandler.decode_token()\`
3. Looks up the user by \`sub\` claim in the database
4. Raises \`401 Unauthorized\` if the token is expired or invalid

Passwords are hashed using **bcrypt** via \`verify_password()\` in \`password.py\`.`,
  },
};

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export interface UseMockDemoReturn {
  state: DemoState;
  start: (query: string) => void;
  reset: () => void;
}

export function useMockDemo(): UseMockDemoReturn {
  const [state, dispatch] = useReducer(reducer, initialState);
  const timeoutsRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const clearTimeouts = () => {
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];
  };

  const schedule = (fn: () => void, delay: number) => {
    const id = setTimeout(fn, delay);
    timeoutsRef.current.push(id);
  };

  const start = useCallback((query: string) => {
    clearTimeouts();
    dispatch({ type: "START", query });

    const mock = MOCK_RESULTS["default"];
    let t = 0;

    // Phase 1: Type the query character by character
    for (let i = 0; i < query.length; i++) {
      const char = query[i];
      const delay = i * 38 + Math.random() * 15;
      t = Math.max(t, delay);
      schedule(() => dispatch({ type: "TYPE_CHAR", char }), delay);
    }

    // Phase 2: Planning
    t += 180;
    schedule(() => dispatch({ type: "ADVANCE_PHASE", phase: "planning" }), t);

    // Phase 3: Searching + stream results
    t += 700;
    schedule(() => dispatch({ type: "ADVANCE_PHASE", phase: "searching" }), t);
    mock.results.forEach((result, i) => {
      schedule(() => dispatch({ type: "ADD_RESULT", result }), t + 220 + i * 180);
    });
    t += 220 + mock.results.length * 180;

    // Phase 4: Building context
    schedule(() => dispatch({ type: "ADVANCE_PHASE", phase: "building" }), t);
    mock.context.forEach((file, i) => {
      schedule(() => dispatch({ type: "ADD_CONTEXT", file }), t + 150 + i * 150);
    });
    t += 150 + mock.context.length * 150 + 200;

    // Phase 5: Answering — stream character by character
    schedule(() => dispatch({ type: "ADVANCE_PHASE", phase: "answering" }), t);
    const answer = mock.answer;
    for (let i = 0; i < answer.length; i++) {
      const char = answer[i];
      schedule(() => dispatch({ type: "TYPE_ANSWER_CHAR", char }), t + 50 + i * 12);
    }
    t += 50 + answer.length * 12;

    // Done
    schedule(() => dispatch({ type: "ADVANCE_PHASE", phase: "done" }), t + 200);
  }, []);

  const reset = useCallback(() => {
    clearTimeouts();
    dispatch({ type: "RESET" });
  }, []);

  useEffect(() => () => clearTimeouts(), []);

  return { state, start, reset };
}
