import easyocr
import langcodes
import language_tool_python

tool = None


def grammar_enhance(text):
    matches = tool.check(text)
    my_mistakes = []
    my_corrections = []
    start_positions = []
    end_positions = []

    for rules in matches:
        if len(rules.replacements) > 0:
            start_positions.append(rules.offset)
            end_positions.append(rules.errorLength + rules.offset)
            my_mistakes.append(text[rules.offset:rules.errorLength + rules.offset])
            my_corrections.append(rules.replacements[0])

    my_new_text = list(text)

    for m in range(len(start_positions)):
        for i in range(len(text)):
            my_new_text[start_positions[m]] = my_corrections[m]
            if start_positions[m] < i < end_positions[m]:
                my_new_text[i] = ""

    my_new_text = "".join(my_new_text)
    return my_new_text


def get_text_from_img(img, tlang):
    global tool
    tool = language_tool_python.LanguageTool(str(langcodes.find(tlang)))
    reader = easyocr.Reader([str(langcodes.find(tlang))], gpu=False)
    results = reader.readtext(img, detail=1, paragraph=False)
    words = []
    corrected_words = []
    for i in range(len(results)):
        words.append(results[i][1])

    for i in range(0, len(words)):
        if not words[i].isalpha():
            for j in range(0, len(words[i])):
                if not words[i][j].isalpha() and words[i][j] not in ' -\'&#^':
                    words[i] = words[i][:j - 1]
                    break
        corrected_words.append(grammar_enhance(words[i]))
    return corrected_words