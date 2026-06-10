import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import "./BackLink.css";

export function BackLink() {
  return (
    <Link className="back-link" to="/">
      <ArrowLeft size={18} strokeWidth={2.2} />
      <span>На главную</span>
    </Link>
  );
}
