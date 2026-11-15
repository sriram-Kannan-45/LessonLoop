# Native teaching languages

The Lesson language selector controls lesson generation and evaluation. It does not translate the whole application interface. Supported codes are en English, ta Tamil, hi Hindi, te Telugu, kn Kannada, ml Malayalam, mr Marathi, bn Bengali, gu Gujarati and pa Punjabi. English remains the default for old clients and historical runs.

Choose **தமிழ் · Tamil**, enter a topic such as Introduction to RAG, leave the error demonstration off, and Generate once. Prefer a specific English topic name for reference discovery; choosing Tamil changes the teaching language independently of the search topic.

## Guarantees enforced by code

- The requested code is validated against the supported list and stored on the run. Existing SQLite records migrate to en because they were generated under the earlier English-only contract.
- Native runs save a versioned localized generator prompt and evaluator version. Their frozen rubric adds a mandatory LANGUAGE model check: explanations, examples, recap and practice must use the selected native script and simple words.
- All checks still must pass. English has 14; native-language runs have 15. Wrong-language output cannot approve when LANGUAGE fails. The evaluator can still make an incorrect judgment, so this is not independent linguistic certification.
- JSON keys, source/claim identifiers, URLs and evidence paths remain stable. Original source quotations may stay in their original language; their meaning must be taught in the selected language. English technical terms need a local plain-language explanation.
- English learned instructions are excluded from native runs. Native observations do not qualify the English reviewed-RAG calibration. Cross-language prompt improvement requires its own reviewed data and validation; it is not implemented by pooling unrelated failures.
- Cancellation, retry limits, source validation, exact evidence and unapproved export labelling remain unchanged.

## Downloads

TXT preserves UTF-8 and DOCX preserves Unicode with a native-script font preference. Windows PDF rendering uses Nirmala UI with HarfBuzz shaping for Indic scripts. Another deployment needs a suitable installed font or the process environment variable LESSONLOOP_PDF_FONT pointing to a matching TrueType font. Missing font support gives an explicit error; use TXT or Word instead. One font may not cover every selected script, so deployers must check their target fonts.

## Evidence and limits

Automated tests cover persistence, native prompt/rubric plumbing, wrong-language rejection across all three drafts, default English compatibility, API validation, UI selection and Unicode exports. An authored Tamil font sample was visually inspected as PDF; it is not a generated lesson-quality benchmark. The real Tamil RAG diagnostic attempted on 15 November stopped because the configured local FreeLLM router was unreachable. Successful live Tamil generation/evaluation remains pending; the application does not fabricate that result. Other native-language linguistic accuracy has not been independently reviewed.

The original take-home submission still uses Introduction to RAG. English is the demonstrated historical submission language. Native teaching is an additional accessibility feature, not a claim that all assessment deliverables or self-evolution acceptance are finished.

## தமிழில் பயன்படுத்துவது

1. Topic இடத்தில் Introduction to RAG போன்ற தலைப்பை உள்ளிடுங்கள்.
2. Lesson language பகுதியில் தமிழ் தேர்வு செய்யுங்கள்.
3. சாதாரண பாடத்திற்கு Inject a factual error தேர்வை அணைத்து வையுங்கள்.
4. Generate அழுத்தி இறுதி முடிவு வரும் வரை காத்திருங்கள்.
5. Approved வந்தால் பாடத்தைப் படித்து பதிவிறக்கலாம். Needs review வந்தால் Quality report பகுதியில் மீதமுள்ள பிரச்சினைகளைப் பாருங்கள்.

மூல ஆதார மேற்கோள்கள் ஆங்கிலத்தில் இருக்கலாம். பாட விளக்கமும் பயிற்சி வினாக்களும் தேர்வு செய்த மொழியில் இருக்க வேண்டும். Live Tamil சோதனைக்கு உள்ளூர் FreeLLM சேவை இயங்க வேண்டும்.
