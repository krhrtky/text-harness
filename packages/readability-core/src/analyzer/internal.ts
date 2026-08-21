import { type SourceRange } from "../types/range.ts";

export type InternalTokenRole = "leading" | "predicate" | "demonstrative" | "terminal";

export type InternalToken = Readonly<{
  surfaceForm: string;
  lemma: string;
  role: InternalTokenRole;
  range: SourceRange;
  morphologyLabel?: string;
}>;

export type InternalSentenceAnalysis = Readonly<{
  tokens: readonly InternalToken[];
  predicateGroupCount: number;
  demonstrativeLemmas: readonly string[];
  leadingSurfaceLabel?: string;
  terminalMorphologyLabel?: string;
}>;

type LocalMatch = Readonly<{ surface: string; lemma: string; start: number; end: number }>;

const LEADING_OPEN = /^[\s「『（【\[(]+/u;
const LEADING_LABEL = /^(?:そのため|しかし|または|そして|ところで|一方|まず|次に|また|さらに|これら|それら|あれら|あそこ|これ|それ|あれ|この|その|あの|ここ|そこ|こう|そう|ああ|[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}ー]+?)(?=[、，,\s]|$)/u;
const CLAUSE = /[^、，,；;]+/gu;
const TERMINAL_MARKS = /[\s。．.!！?？…」』）】\]]+$/u;
const PARTICLE_BOUNDARY = new Set(["は", "が", "を", "に", "で", "と", "の", "も", "へ", "や", "、", "，", ",", "。", "！", "？", "!", "?", " ", "\n", "\t"]);
const OPEN_BOUNDARY = new Set(["「", "『", "（", "【", "[", "、", "，", ",", "。", "！", "？", "!", "?", " ", "\n", "\t"]);
const PRONOUNS = ["これら", "それら", "あれら", "あそこ", "これ", "それ", "あれ", "ここ", "そこ"] as const;
const DETERMINERS = ["この", "その", "あの"] as const;
const ADVERBS = ["こう", "そう", "ああ"] as const;
const ADVERB_FOLLOWERS = new Set(["し", "な", "だ", "で", "言", "考", "思", "見", "話", "書", "読", "行", "進", "変", "、", "。", "！", "？", "!", "?", " "]);
const PRECEDING_PARTICLES = new Set(["は", "が", "を", "に", "で", "と", "の", "も", "へ", "や"]);
const CONJUNCTIVE_PREDICATES: Readonly<Record<string, string>> = Object.freeze({
  読み: "読む", 書き: "書く", 考え: "考える", 調べ: "調べる", 説明し: "説明する",
  確認し: "確認する", 実行し: "実行する", 利用し: "利用する", 検討し: "検討する",
  使い: "使う", 作り: "作る", 行い: "行う", 進め: "進める", 比べ: "比べる",
});
const ADJECTIVE_FORMS: Readonly<Record<string, Readonly<{ lemma: string; form: "plain-nonpast" | "plain-past" }>>> = Object.freeze({
  美しくない: { lemma: "美しい", form: "plain-nonpast" }, 難しくない: { lemma: "難しい", form: "plain-nonpast" },
  易しくない: { lemma: "易しい", form: "plain-nonpast" }, 少なくない: { lemma: "少ない", form: "plain-nonpast" },
  美しかった: { lemma: "美しい", form: "plain-past" }, 難しかった: { lemma: "難しい", form: "plain-past" },
  易しかった: { lemma: "易しい", form: "plain-past" }, 高かった: { lemma: "高い", form: "plain-past" },
  低かった: { lemma: "低い", form: "plain-past" }, 美しい: { lemma: "美しい", form: "plain-nonpast" },
  難しい: { lemma: "難しい", form: "plain-nonpast" }, 易しい: { lemma: "易しい", form: "plain-nonpast" },
  少ない: { lemma: "少ない", form: "plain-nonpast" }, 新しい: { lemma: "新しい", form: "plain-nonpast" },
  古い: { lemma: "古い", form: "plain-nonpast" }, 高い: { lemma: "高い", form: "plain-nonpast" },
  低い: { lemma: "低い", form: "plain-nonpast" }, 長い: { lemma: "長い", form: "plain-nonpast" },
  短い: { lemma: "短い", form: "plain-nonpast" }, 良い: { lemma: "良い", form: "plain-nonpast" },
  悪い: { lemma: "悪い", form: "plain-nonpast" }, 多い: { lemma: "多い", form: "plain-nonpast" },
  ない: { lemma: "ない", form: "plain-nonpast" },
});
const PLAIN_VERB_FORMS: Readonly<Record<string, Readonly<{ lemma: string; form: "plain-nonpast" | "plain-past" }>>> = Object.freeze({
  読む: { lemma: "読む", form: "plain-nonpast" }, 読んだ: { lemma: "読む", form: "plain-past" },
  書く: { lemma: "書く", form: "plain-nonpast" }, 書いた: { lemma: "書く", form: "plain-past" },
  考える: { lemma: "考える", form: "plain-nonpast" }, 考えた: { lemma: "考える", form: "plain-past" },
  調べる: { lemma: "調べる", form: "plain-nonpast" }, 調べた: { lemma: "調べる", form: "plain-past" },
  確認する: { lemma: "確認する", form: "plain-nonpast" }, 確認した: { lemma: "確認する", form: "plain-past" },
  説明する: { lemma: "説明する", form: "plain-nonpast" }, 説明した: { lemma: "説明する", form: "plain-past" },
  使う: { lemma: "使う", form: "plain-nonpast" }, 使った: { lemma: "使う", form: "plain-past" },
  見る: { lemma: "見る", form: "plain-nonpast" }, 見た: { lemma: "見る", form: "plain-past" },
  話す: { lemma: "話す", form: "plain-nonpast" }, 話した: { lemma: "話す", form: "plain-past" },
});

function token(surfaceForm: string, lemma: string, role: InternalTokenRole, start: number, baseOffset: number, morphologyLabel?: string): InternalToken {
  const base = {
    surfaceForm,
    lemma,
    role,
    range: Object.freeze({ start: baseOffset + start, end: baseOffset + start + surfaceForm.length }),
  };
  return Object.freeze(morphologyLabel === undefined ? base : { ...base, morphologyLabel });
}

function previousIsBoundary(text: string, index: number): boolean {
  const previous = text[index - 1] ?? "";
  return index === 0 || OPEN_BOUNDARY.has(previous) || PRECEDING_PARTICLES.has(previous);
}

function nextIsBoundary(text: string, index: number): boolean {
  return index === text.length || PARTICLE_BOUNDARY.has(text[index] ?? "");
}

function demonstratives(text: string): readonly LocalMatch[] {
  const matches: LocalMatch[] = [];
  for (let index = 0; index < text.length; index += 1) {
    const pronoun = PRONOUNS.find((candidate) => text.startsWith(candidate, index)
      && previousIsBoundary(text, index) && nextIsBoundary(text, index + candidate.length));
    const determiner = DETERMINERS.find((candidate) => text.startsWith(candidate, index)
      && previousIsBoundary(text, index));
    const adverb = ADVERBS.find((candidate) => text.startsWith(candidate, index)
      && previousIsBoundary(text, index) && ADVERB_FOLLOWERS.has(text[index + candidate.length] ?? " "));
    const lemma = pronoun ?? determiner ?? adverb;
    if (lemma !== undefined) {
      matches.push({ surface: lemma, lemma, start: index, end: index + lemma.length });
      index += lemma.length - 1;
    }
  }
  return matches;
}

function predicateAtClauseEnd(clause: string, clauseStart: number): LocalMatch | undefined {
  const withoutTerminal = clause.replace(TERMINAL_MARKS, "").trimEnd();
  const polite = withoutTerminal.match(/([\p{Script=Han}\p{Script=Katakana}ー]+)(できませんでした|できました|できます|しませんでした|しました|しません|します|して|した|する)$/u);
  if (polite?.index !== undefined) {
    const stem = polite[1] ?? "";
    const surface = polite[0];
    const lemma = polite[2]?.startsWith("でき") ? `${stem}できる` : `${stem}する`;
    return { surface, lemma, start: clauseStart + polite.index, end: clauseStart + polite.index + surface.length };
  }
  const generalPolite = withoutTerminal.match(/(ませんでした|ました|ません|ます)$/u);
  if (generalPolite?.index !== undefined) {
    const stem = lexicalStem(withoutTerminal.slice(0, generalPolite.index));
    if (stem.length > 0) {
      const surface = `${stem}${generalPolite[0]}`;
      const start = clauseStart + withoutTerminal.length - surface.length;
      return { surface, lemma: lemmaFromPoliteStem(stem), start, end: start + surface.length };
    }
  }
  const copula = withoutTerminal.match(/(でした|だった|である|です|だ)$/u);
  if (copula?.index !== undefined) {
    const surface = copula[0];
    return { surface, lemma: surface.startsWith("で") ? "です" : "だ", start: clauseStart + copula.index, end: clauseStart + copula.index + surface.length };
  }
  const conjunctive = Object.entries(CONJUNCTIVE_PREDICATES).find(([surface]) => withoutTerminal.endsWith(surface));
  if (conjunctive !== undefined) {
    const [surface, lemma] = conjunctive;
    const start = clauseStart + withoutTerminal.length - surface.length;
    return { surface, lemma, start, end: start + surface.length };
  }
  const adjective = Object.keys(ADJECTIVE_FORMS)
    .find((surface) => withoutTerminal.endsWith(surface));
  if (adjective !== undefined) {
    const start = clauseStart + withoutTerminal.length - adjective.length;
    return { surface: adjective, lemma: adjective, start, end: start + adjective.length };
  }
  const plainVerb = withoutTerminal.match(/([\p{Script=Han}\p{Script=Katakana}ー]+(?:読む|書く|考える|調べる|使う|作る|行う|進む|進める|比べる|見る|話す))$/u);
  if (plainVerb?.index !== undefined) {
    return { surface: plainVerb[0], lemma: plainVerb[0], start: clauseStart + plainVerb.index, end: clauseStart + plainVerb.index + plainVerb[0].length };
  }
  return undefined;
}

function predicates(text: string): readonly LocalMatch[] {
  return [...text.matchAll(CLAUSE)].flatMap((match) => {
    const predicate = predicateAtClauseEnd(match[0], match.index);
    return predicate === undefined ? [] : [predicate];
  });
}

function lexicalStem(text: string): string {
  return text.split(/[はがをにでともへ]/u).at(-1) ?? text;
}

function lemmaFromPoliteStem(stem: string): string {
  const known: Readonly<Record<string, string>> = {
    読み: "読む", 書き: "書く", 話し: "話す", 使い: "使う", 行い: "行う",
    進み: "進む", 調べ: "調べる", 考え: "考える", 見: "見る", 比べ: "比べる",
  };
  if (known[stem] !== undefined) return known[stem];
  if (stem.endsWith("でき")) return `${stem.slice(0, -2)}できる`;
  return stem.endsWith("し") ? `${stem.slice(0, -1)}する` : stem;
}

function leading(text: string): LocalMatch | undefined {
  const prefixLength = text.match(LEADING_OPEN)?.[0].length ?? 0;
  const match = text.slice(prefixLength).match(LEADING_LABEL);
  return match === null
    ? undefined
    : { surface: match[0], lemma: match[0], start: prefixLength, end: prefixLength + match[0].length };
}

function terminal(text: string): Readonly<{ match: LocalMatch; label: string }> | undefined {
  const withoutMarks = text.replace(TERMINAL_MARKS, "");
  const particleMatch = withoutMarks.match(/([かねよぞ])$/u);
  const particle = particleMatch?.[1];
  const body = particle === undefined ? withoutMarks : withoutMarks.slice(0, -particle.length);
  const forms = [
    { suffix: "ませんでした", form: "polite-negative-past" },
    { suffix: "ました", form: "polite-past" },
    { suffix: "ません", form: "polite-negative-nonpast" },
    { suffix: "ます", form: "polite-nonpast" },
  ] as const;
  const compound = forms.find(({ suffix }) => body.endsWith(suffix));
  if (compound !== undefined) {
    const before = body.slice(0, -compound.suffix.length);
    const stem = lexicalStem(before);
    const surface = `${stem}${compound.suffix}`;
    const lemma = lemmaFromPoliteStem(stem);
    const label = `verb:${lemma}:${compound.form}${particle === undefined ? "" : `|particle:${particle}`}`;
    const start = body.length - surface.length;
    return { match: { surface, lemma, start, end: start + surface.length }, label };
  }
  const copulas = [
    { suffix: "でした", lemma: "です", form: "polite-past" },
    { suffix: "だった", lemma: "だ", form: "plain-past" },
    { suffix: "です", lemma: "です", form: "polite-nonpast" },
    { suffix: "だ", lemma: "だ", form: "plain-nonpast" },
  ] as const;
  const hasPlainVerbEnding = Object.keys(PLAIN_VERB_FORMS).some((surface) => body.endsWith(surface));
  const copula = hasPlainVerbEnding ? undefined : copulas.find(({ suffix }) => body.endsWith(suffix));
  if (copula !== undefined) {
    const start = body.length - copula.suffix.length;
    const label = `copula:${copula.lemma}:${copula.form}${particle === undefined ? "" : `|particle:${particle}`}`;
    return { match: { surface: copula.suffix, lemma: copula.lemma, start, end: body.length }, label };
  }
  const adjective = Object.entries(ADJECTIVE_FORMS).find(([surface]) => body.endsWith(surface));
  if (adjective !== undefined) {
    const [surface, morphology] = adjective;
    const start = body.length - surface.length;
    const label = `adjective:${morphology.lemma}:${morphology.form}${particle === undefined ? "" : `|particle:${particle}`}`;
    return { match: { surface, lemma: morphology.lemma, start, end: body.length }, label };
  }
  const plainVerb = Object.entries(PLAIN_VERB_FORMS).find(([surface]) => body.endsWith(surface));
  if (plainVerb === undefined) return undefined;
  const [surface, morphology] = plainVerb;
  const start = body.length - surface.length;
  const label = `verb:${morphology.lemma}:${morphology.form}${particle === undefined ? "" : `|particle:${particle}`}`;
  return { match: { surface, lemma: morphology.lemma, start, end: body.length }, label };
}

export function analyzeInternalSentence(text: string, baseOffset = 0): InternalSentenceAnalysis {
  const predicateMatches = predicates(text);
  const demonstrativeMatches = demonstratives(text);
  const leadingMatch = leading(text);
  const terminalMatch = terminal(text);
  const tokens = [
    ...(leadingMatch === undefined ? [] : [token(leadingMatch.surface, leadingMatch.lemma, "leading", leadingMatch.start, baseOffset)]),
    ...predicateMatches.map((match) => token(match.surface, match.lemma, "predicate", match.start, baseOffset)),
    ...demonstrativeMatches.map((match) => token(match.surface, match.lemma, "demonstrative", match.start, baseOffset)),
    ...(terminalMatch === undefined ? [] : [token(terminalMatch.match.surface, terminalMatch.match.lemma, "terminal", terminalMatch.match.start, baseOffset, terminalMatch.label)]),
  ].sort((left, right) => left.range.start - right.range.start || (left.role < right.role ? -1 : left.role > right.role ? 1 : 0));
  return Object.freeze({
    tokens: Object.freeze(tokens),
    predicateGroupCount: predicateMatches.length,
    demonstrativeLemmas: Object.freeze(demonstrativeMatches.map(({ lemma }) => lemma)),
    ...(leadingMatch === undefined ? {} : { leadingSurfaceLabel: leadingMatch.surface }),
    ...(terminalMatch === undefined ? {} : { terminalMorphologyLabel: terminalMatch.label }),
  });
}
