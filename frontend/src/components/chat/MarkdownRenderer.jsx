import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useState } from "react";
import { Copy, Check } from "lucide-react";

function CodeBlock({ language, value }) {
  const [copied, setCopied] = useState(false);

  const copyCode = async () => {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-4 overflow-hidden rounded-2xl border border-gray-800 bg-[#0d1117] shadow-xl">
      <div className="flex items-center justify-between border-b border-gray-800 bg-gray-900/90 px-4 py-2 text-xs text-gray-400">
        <span className="font-mono text-[11px] font-bold uppercase tracking-wider text-emerald-400">
          {language || "code"}
        </span>
        <button
          type="button"
          onClick={copyCode}
          className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-[11px] font-semibold text-gray-400 transition hover:bg-gray-800 hover:text-white"
        >
          {copied ? (
            <>
              <Check size={13} className="text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy size={13} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <SyntaxHighlighter
        style={oneDark}
        language={language || "text"}
        PreTag="div"
        customStyle={{
          margin: 0,
          padding: "1.25rem",
          fontSize: "0.875rem",
          lineHeight: "1.6",
          background: "transparent",
        }}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  );
}

export default function MarkdownRenderer({ content }) {
  return (
    <div className="prose prose-invert max-w-none text-base leading-relaxed text-gray-200">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1({ children }) {
            return (
              <h1 className="mt-4 mb-3 pb-2 text-xl font-extrabold tracking-tight text-white border-b border-gray-800 sm:text-2xl">
                {children}
              </h1>
            );
          },
          h2({ children }) {
            return (
              <h2 className="mt-5 mb-2.5 text-lg font-bold text-emerald-400 tracking-wide">
                {children}
              </h2>
            );
          },
          h3({ children }) {
            return (
              <h3 className="mt-4 mb-2 text-base font-semibold text-indigo-300">
                {children}
              </h3>
            );
          },
          h4({ children }) {
            return (
              <h4 className="mt-3 mb-1.5 text-sm font-semibold text-gray-200">
                {children}
              </h4>
            );
          },
          p({ children }) {
            return <p className="mb-2 text-base leading-relaxed text-gray-200">{children}</p>;
          },
          ul({ children }) {
            return <ul className="my-2 ml-5 list-disc list-outside space-y-1 text-base leading-relaxed text-gray-200">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="my-2 ml-5 list-decimal list-outside space-y-1 text-base leading-relaxed text-gray-200">{children}</ol>;
          },
          li({ children }) {
            return <li className="pl-1 leading-relaxed">{children}</li>;
          },
          blockquote({ children }) {
            return (
              <blockquote className="my-4 rounded-r-2xl border-l-4 border-emerald-500 bg-emerald-500/10 px-4 py-3 text-sm italic text-emerald-200">
                {children}
              </blockquote>
            );
          },
          hr() {
            return <hr className="my-6 border-gray-800" />;
          },
          strong({ children }) {
            return <strong className="font-bold text-white">{children}</strong>;
          },
          em({ children }) {
            return <em className="italic text-gray-300">{children}</em>;
          },
          code({ inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const codeString = String(children).replace(/\n$/, "");

            return !inline && match ? (
              <CodeBlock language={match[1]} value={codeString} />
            ) : (
              <code className="rounded-lg bg-gray-800/90 px-1.5 py-0.5 font-mono text-xs text-emerald-300 border border-gray-700/60" {...props}>
                {children}
              </code>
            );
          },
          table({ children }) {
            return (
              <div className="my-5 overflow-x-auto rounded-2xl border border-gray-800 bg-gray-950/80 shadow-lg">
                <table className="w-full text-left text-sm text-gray-200">{children}</table>
              </div>
            );
          },
          th({ children }) {
            return <th className="border-b border-gray-800 bg-gray-900/90 px-4 py-2.5 font-bold text-white text-xs uppercase tracking-wider">{children}</th>;
          },
          td({ children }) {
            return <td className="border-b border-gray-800/60 px-4 py-2.5">{children}</td>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}