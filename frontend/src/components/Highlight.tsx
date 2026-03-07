"use client";

import { useEffect } from "react";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";

export default function Highlight() {
  useEffect(() => {
    hljs.highlightAll();
  }, []);
  return null;
}
