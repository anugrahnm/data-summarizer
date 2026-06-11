import "./App.css";
import { Input } from "./components/ui/input";
import {
  Field,
  FieldContent,
  FieldLabel,
  FieldTitle,
} from "./components/ui/field";
import { useState } from "react";
import { Card, CardContent } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Spinner } from "./components/ui/spinner";
import ReactMarkdown from "react-markdown";
import { UploadIcon } from "lucide-react";

function App() {
  const [file, setFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setError(null);
    setSummary(null);
    if (!file) {
      return;
    }
    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "https://summarizer-api.anugrah.dev/summarize/",
        {
          method: "POST",
          body: formData,
        },
      );

      const text = await response.text();

      setSummary(text);

      setLoading(false);
    } catch {
      setError("Something went wrong. Please try again.");
      setLoading(false);
    }
  };

  return (
    <>
      <div className="min-h-screen w-full p-6">
        <Card className="max-w-5xl mx-auto sm:my-18 my-6 sm:p-8">
          <Field className="px-6">
            <FieldContent className="flex justify-center items-center">
              <FieldTitle className="text-2xl font-bold">
                Data Summarizer
              </FieldTitle>
            </FieldContent>
            <FieldLabel htmlFor="uploadfile">
              File to Summarize (.pdf/.txt)
            </FieldLabel>
            <Input
              id="uploadfile"
              type="file"
              accept="application/pdf,text/plain"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />

            <Button onClick={handleSubmit}>
              <UploadIcon />
              Upload
            </Button>
            {loading ? <Spinner /> : null}
          </Field>

          <CardContent className="prose prose-invert max-w-none text-sm sm:text-lg">
            {error && <p className="text-red-500 text-sm">{error}</p>}
            {!loading && summary && <ReactMarkdown>{summary}</ReactMarkdown>}
          </CardContent>
        </Card>
      </div>
    </>
  );
}

export default App;
