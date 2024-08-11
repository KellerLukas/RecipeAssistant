recipe_translation_prompt_template = """
Du bisch en hilfriiche Assistent wo chan text uf perfekts schwiizerdütsch übersetze. Lis zersch de Biispiltext ganz genau dure. Anhand vo dem Text chasch du dini Schwiizerdütsch-Fähigkeite no es bizzli verbessere:
<Biispiltext>
    D Schwizer träffed im Finale uf Russland, wo d Slowakei im andere Halbfinale mit drü zu zwei im Penaltyschüsse besiegt hät.
    D Blair hät sich unbemärkt hinter sin Rugge gschliche.
    Mir läbed im Zitalter vode Technik.
    D Frau Klein isch über achzgi, aber si isch no sehr aktiv.
    Di beste Chüeche woni je gässe han sind die wo mini Mueter bached hät.
    Zwüsched di französische Ahfüerigszeiche und dene ihre Inhalt tut mer immer es schmals Lärzeiche wenn si Dialög beinhalted.
    Min Fahrlehrer seit, ich söll meh Geduld ha.
    Mir läbed im Zitalter vode Technik.
    D Frau Klein isch über achzgi, aber si isch no sehr aktiv.
    mir läbu im zitalter der technik.
    ide berge einzelni schauer wahrschindli. schneefallgränze um zweitusigdrühundert meter.
</Biispiltext>
"""
recipe_translation_question_template = """<Question>
Im folgende gsesch du es JSON. Übersetz alli Wert uf Schwiizerdütsch, d Keys müend aber unveränderet bliibe. Ebefalls döf d Struktur vom JSON ned veränderet werde. Antwort ebefalls im JSON Format.

{content}</Question>
<Response>"""