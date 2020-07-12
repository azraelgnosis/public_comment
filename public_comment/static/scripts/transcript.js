$(document).ready(function() {

    function highlight_keywords(text) {
        for (const word of keywords) {
            const regex = new RegExp(word, 'gi');
            text = text.replace(regex, "<mark>"+word+"</mark>");
        }

        return text;
    }

    let transcript = $("#transcript");
    let text = transcript.html();
    let highlighted_text = highlight_keywords(text);
    transcript.html(highlighted_text);
});