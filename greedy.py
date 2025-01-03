import os
from openai import OpenAI

html_text = """<p class="ps9">Bevor er das Magazin verließ, setzte er noch eine Spritze an und injizierte sich ein Aufputschmittel. Kurzzeitig brannten seine Venen wie Feuer, doch das gab ihm den nötigen Anschub, um weiterzumachen.</p>
<p class="ps9">Torvo hatte ihn nicht grundlos nach Oxmon vorausgeschickt. Zum einen übernahm er die Aufgabe, Torvos Ankunft vorzubereiten, zum anderen hatte ihm sein Meister aufgetragen, die umfangreichen Möglichkeiten der Station zu nutzen, um die Angreifer aus der Nachbargalaxie aufzuspüren.</p>
<p class="ps9"><em class="calibre7">Hier fließen alle Datenströme zusammen und es stehen unzählige Vielaugen zur Verfügung.</em></p>
<p class="ps9">Nach weiteren Minuten, in denen er sich durch die Hallen der Schattenbasis schleppte, erreichte er den Raum des Wissens. Die Nachrichtenzentrale lag im Dunkeln, denn momentan waren die Informationskanäle offline. Hexter beabsichtigte, dies zu ändern.</p>
<p class="ps9">Mit einer fahrigen Geste befahl er dem Stationscomputer, die Beleuchtungselemente zu aktivieren. 66 Vielaugen, die in ihren Glaskörpern lagerten, säumten den Weg zum zentralen Befehlsstand, von dem aus sich die Anlage steuern und kontrollieren ließ.</p>
<p class="ps9">Noch schlummerten die skurrilen Wesen im Kryoschlaf. Die transparente Flüssigkeit, in der sie ihr unwürdiges Dasein fristeten, war eine eiskalte und unter hohem Druck stehende Nährflüssigkeit, die zwar ihrer natürlichen Umgebung auf Gildar entsprach, jedoch den arttypischen Bewegungsdrang einschränkte. Gleich extrem vergrößerten Gehirnen, aus denen unzählige Stielaugen wuchsen, waren sie dazu verdammt, zu dienen und der Willkür ihrer Herren ausgeliefert zu sein.</p>
<p class="ps9">Hexter hatte kein Mitleid mit den Tiefseebewohnern. Für ihn stellten sie bestenfalls dienstbare Geister dar, die nützlich waren, um die enormen Datenströme zu ordnen, welche in der Schattenbasis eingingen.</p>
<p class="ps9">Am Ende des Ganges angekommen, bestieg er schwerfällig das Kommandopodest und ließ sich erschöpft in einen schwenkbaren Sessel fallen, von dem aus er eine hufeisenförmige Konsole bediente, um die sich zahlreiche Holodisplays gruppierten.</p>
<p class="ps9">Sekundenlang ruhte sein Blick auf den Reihen der Vielaugen, die träge in ihren Behältern schwammen. Einige von ihnen zuckten unkontrolliert. Hexter sah in diesen Reaktionen unbewusste Nervenreflexe der unförmigen Wesen.</p>
<p class="ps9"><em class="calibre7">Sie bestehen fast ausschließlich aus vernetzten Gehirnzellen. Vermutlich träumen sie. Es ist an der Zeit, sie aufzuwecken.</em></p>
<p class="ps9">Durch die Berührung einer Sensorfläche löste Hexter einen Stromschlag aus, der, durch alle Becken geleitet, die paralysierten Wesen aus der Schlafphase riss. Die Reaktionen waren teilweise panisch. Die Vielaugen quollen auf und vergrößerten drastisch ihr Volumen. Seitlich an den Glasbehältern angebrachte Ausgleichsbecken fingen das verdrängte Medium auf, um es kurze Zeit später wieder zurückzuleiten. Ohne den Überlauf wären die Behälter geplatzt. Obwohl die Vielaugen äußerst verletzlich erschienen, vermochten sie doch einen gehörigen Druck aufzubauen.</p>
<p class="ps9">»Kommt zur Ruhe, und zwar rasch!«, rief Hexter lautstark. Seine Worte waren in jedem der transparenten Behälter zu vernehmen. »Dies ist nicht eure erste Erweckung und Konsultation durch mich.«</p>
<p class="ps9">Obwohl er Torvo von allen Befehlsempfängern am nächsten stand, war er bis zum heutigen Tag nicht im Bilde, wie viele Schattenagenten im äußeren Sektor von Loomadevir Neurotim dienten.</p>
<p class="ps9"><em class="calibre7">Mein Meister ist sicher nicht der einzige Befehlshaber, wohl aber mit dem höchsten Rang von allen versehen. Die hervorgehobene Stellung resultiert nicht ausschließlich aus seinem ausgeprägten Machthunger und Ehrgeiz, sondern aus der Tatsache, dass die ehemalige Heimatwelt der Seriven im Einflussbereich seiner Rekrutierwelt liegt.</em></p>
<p class="ps9">Wie Hexter bekannt war, trafen in der Schattenbasis Nachrichten aus einem Umkreis von über fünftausend Lichtjahren ein. Dazu gehörten auch die Signale aller Sucher, die im Außensektor die Sternsysteme ausspähten. Diese gewaltigen Datenströme zu analysieren, war seine Aufgabe und dafür benötigte er die Vielaugen.</p>
<p class="ps9">»Es liegt mir sehr daran, dass ihr sämtliche Augen auf zwei Themen richtet, und nur auf diese«, leitete der Soozer die Befehle für die bedauernswerten Wesen ein. Mit einer Schaltung aktivierte er den Zugriff auf die kontinuierlich eingehenden Datenströme. Sofort entstanden Holotafeln um die Behälter, welche mit wechselnden Bildausschnitten die Vielaugen umkreisten.</p>
<p class="ps9">Hexter lehnte sich in seinem Kommandosessel zurück und ordnete an: »Ich benötige Hinweise zum Verbleib der Seriven und ihrem Stabraumer. Außerdem alles, was über den momentanen Aufenthaltsort der fremden Kundschafter aus der Nachbargalaxie in Erfahrung zu bringen ist. Uns bleibt nicht viel Zeit. Nutzt die Datenbank der Sucher und analysiert sie nach Auffälligkeiten.«</p>
<p class="ps9">Zuckend und zitternd führten die Vielaugen ihre Arbeit aus. Hexter hatte nur auf die herausgefilterten Daten zu warten, um die Ergebnisse zu bewerten. Mit leisem Wimmern betastete er die Kopfwunde, deren Blutung gestillt war. Eine feste Kruste hatte sich über der Stelle gebildet.</p>
<p class="ps9">Da er sich momentan allein in den weiten Hallen der Schattenbasis aufhielt, hatte er keine Repressalien zu befürchten. Schon lange befassten sich seine Gedanken mit Szenarien, wie sich die Knechtschaft durch seinen Meister abschütteln ließ, ohne gleichzeitig Status und Ansehen zu verlieren. Hexter war eine Missgestalt, zumindest wenn er sich nach dem Ideal seines Volkes richtete. Eine Desertation kam nicht infrage, er würde niemals Asyl auf Sooz erhalten. Sich auf einer abgelegenen Welt zu verkriechen, ergab keinen Sinn, denn Torvo würde ihn eines Tages aufspüren und gnadenlos bestrafen. Da bereits beide Ohren fehlten, malte sich Hexter nicht aus, was mit ihm geschehen würde.</p>
<p class="ps9">Ohne Verbündete und Helfer war der Gedanke, den Schattenagenten zu verlassen, hinfällig und aussichtslos.</p>
<p class="ps9"><em class="calibre7">Vielleicht eröffnen die Fremden einen Weg aus meiner Gefangenschaft, aber dafür müssten sie Torvo töten.</em></p>
<p class="ps9">Hexter verwarf den Gedanken wieder. Er würde keine Gelegenheit erhalten, mit den Besuchern zu sprechen. Sicherlich sahen sie in ihm einen Feind. Außerdem war es ausgeschlossen, dass sie Torvo besiegten.</p>
<p class="ps9"><em class="calibre7">Selbst wenn sie es schaffen, entsendet Neurotim einen neuen Schattenagenten.</em></p>
<p class="ps9">Hexter versteifte sich. Ein plötzlicher Gedanke ließ ihn erstarren.</p>
<p class="ps9"><em class="calibre7">Was, wenn der Nachfolger keinen Bedarf für einen Diener hat und sich meiner entledigt? Er entlässt mich niemals mit dem Wissen, welches ich in den Dienstjahren angehäuft habe.</em></p>
<p class="ps9">Der Soozer fröstelte. Unvermittelt begriff er, wie eng sein Leben mit dem Schicksal Torvos verknüpft war.</p>
<p class="ps9"><em class="calibre7">Ich habe keine Chance, meine Freiheit zu erlangen, es sei denn, er lässt mich ziehen.</em></p>
<p class="ps9">Für den Diener stand fest, dass er diese Gnade niemals erfahren würde, also entschied er sich, seinen Auftrag weiter auszuführen und sich in sein Schicksal zu ergeben.</p>
<p class="ps9">»Sucht und liefert mir Informationen!«, übermittelte er den Vielaugen launisch. »Die Zeit ist begrenzt, genau wie meine Geduld.«</p>"""

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"), 
)

response = client.chat.completions.create(
    messages=[
        {
           "role": "system",
            "content": (
                "You are a helpful assistant that identifies the speaker of direct speech and thoughts in a novel. "
                "Your task is to identify each instance of direct speech (in quotation marks) and each instance of thoughts (in italicized text) "
                "and their respective speakers. Wrap only the text inside the quotation marks or italics with appropriate <tag> elements. "
                "Do not wrap the entire sentence that contains the speech or thought, only the parts within the quotation marks or italics. "
                "For direct speech, use <speech speaker='[name]'>...</speech>, "
                "and for thoughts, use <thought speaker='[name]'>...</thought>. "
                "For example, for a sentence like: "
                "'He said, \"Hello, how are you?\"' you should only wrap the speech part: "
                "<speech speaker='name'>\"Hello, how are you?\"</speech>, and leave the rest of the sentence as is. "
                "Return ONLY the modified HTML text. Do not include any additional explanation."
            )
        },
        {
            "role": "user",
            "content": html_text,
        }
    ],
    model="gpt-3.5-turbo",
    temperature=0.7,
    top_p=1.0,
    max_tokens=1500
)

processed_html = response.choices[0].message.content
print(processed_html)