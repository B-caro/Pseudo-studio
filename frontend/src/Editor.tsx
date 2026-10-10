import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import { closeBrackets } from "@codemirror/autocomplete";
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands";
import { bracketMatching, indentOnInput, StreamLanguage, syntaxHighlighting, HighlightStyle } from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import { keymap, lineNumbers, highlightActiveLineGutter, EditorView } from "@codemirror/view";
import { tags } from "@lezer/highlight";

const keywords = new Set([
  "inicio", "fin", "leer", "leertexto", "escribir", "si", "entonces", "sino", "finsi",
  "para", "hasta", "paso", "hacer", "finpara", "mientras", "finmientras", "dimension",
  "funcion", "finfuncion", "retornar", "verdadero", "falso", "y", "o", "no",
]);

const pseudoLanguage = StreamLanguage.define({
  token(stream) {
    if (stream.eatSpace()) return null;
    if (stream.match("//")) {
      stream.skipToEnd();
      return "comment";
    }
    if (stream.match(/^"(?:\\.|[^"\\])*"?/)) return "string";
    if (stream.match(/^(?:\d+\.\d+|\d+|\.\d+)/)) return "number";
    if (stream.match(/^(?:==|!=|<=|>=|[=<>+*/%\-()[\],])/)) return "operator";
    if (stream.match(/^[\p{L}_][\p{L}\p{N}_]*/u, true)) {
      const word = stream.current().toLocaleLowerCase("es");
      if (keywords.has(word)) return "keyword";
      return "variableName";
    }
    stream.next();
    return null;
  },
});

const pseudoHighlight = syntaxHighlighting(HighlightStyle.define([
  { tag: tags.keyword, color: "#b44c37", fontWeight: "650" },
  { tag: tags.string, color: "#1d705b" },
  { tag: tags.number, color: "#9b6a12" },
  { tag: tags.comment, color: "#87918e", fontStyle: "italic" },
  { tag: tags.operator, color: "#485f94" },
  { tag: tags.variableName, color: "#253c54" },
]));

const editorTheme = EditorView.theme({
  "&": { height: "100%", backgroundColor: "#fffefa", color: "#263337", fontSize: "13px" },
  ".cm-scroller": { overflow: "auto", fontFamily: "'IBM Plex Mono', 'Cascadia Code', monospace", lineHeight: "1.75" },
  ".cm-gutters": { backgroundColor: "#fffefa", color: "#56635e", border: "none", paddingRight: "8px" },
  ".cm-activeLineGutter": { color: "#3f7a70", backgroundColor: "#eff6f1" },
  ".cm-activeLine": { backgroundColor: "#f5f8f2" },
  ".cm-cursor": { borderLeftColor: "#d2765e" },
  ".cm-selectionBackground, ::selection": { backgroundColor: "#d8ebe3 !important" },
  ".cm-content": { padding: "18px 0 24px" },
});

export type EditorHandle = { focusSpan: (from: number, to?: number) => void };
type Props = { value: string; onChange: (value: string) => void; readOnly?: boolean };

export const Editor = forwardRef<EditorHandle, Props>(function Editor({ value, onChange, readOnly = false }, ref) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const callback = useRef(onChange);
  callback.current = onChange;

  useImperativeHandle(ref, () => ({
    focusSpan(from: number, to = from) {
      const instance = view.current;
      if (!instance) return;
      const start = Math.max(0, Math.min(from, instance.state.doc.length));
      const end = Math.max(start, Math.min(to, instance.state.doc.length));
      instance.dispatch({ selection: { anchor: start, head: end }, scrollIntoView: true });
      instance.focus();
    },
  }), []);

  useEffect(() => {
    if (!host.current) return;
    const state = EditorState.create({
      doc: value,
      extensions: [
        lineNumbers(), highlightActiveLineGutter(), history(), bracketMatching(), closeBrackets(), indentOnInput(),
        pseudoLanguage, pseudoHighlight, editorTheme,
        keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab]),
        EditorView.editable.of(!readOnly),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) callback.current(update.state.doc.toString());
        }),
      ],
    });
    const instance = new EditorView({ state, parent: host.current });
    instance.contentDOM.setAttribute("aria-label", "Código pseudocódigo");
    instance.contentDOM.setAttribute("spellcheck", "false");
    view.current = instance;
    return () => {
      instance.destroy();
      view.current = null;
    };
  }, [readOnly]);

  useEffect(() => {
    const instance = view.current;
    if (!instance || instance.state.doc.toString() === value) return;
    instance.dispatch({ changes: { from: 0, to: instance.state.doc.length, insert: value } });
  }, [value]);

  return <div className="editor-host" ref={host} />;
});
