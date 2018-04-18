import sys
from lxml import etree
import collections
import glob

def get_format_brat(input_file, outfile1, outfile2):


    doc = etree.parse(input_file, etree.XMLParser(remove_blank_text=True))
    root = doc.getroot()
    root.getchildren()

    token_offset = {}
    sentence_tokens = collections.defaultdict(list)
    sentence_token_id = collections.defaultdict(list)
    token_string_dict = {}


    token_string_ = []
#    counter = -1
    for elem in root.findall('token'):
        token_id = elem.attrib.get('t_id', 'null')
        sentence_id = elem.attrib.get('sentence', 'null')
        token_per_sentence = elem.attrib.get('number', 'null')
        token_string = elem.text
        sentence_tokens[int(sentence_id)].append(token_string)
        sentence_token_id[sentence_id].append(token_id)
        token_string_dict[token_id] = token_string

        token_string_.append(token_string)

    counter = 0
    offsets = []

    for cntr, word in enumerate(token_string_):
        word_offset = word.index(word, counter)
        word_len = len(word)
        running_offset = word_offset + word_len
        offsets.append((cntr, word, word_offset, running_offset))

    full_offset = []
    last_item = None

    for elem in offsets:
        data = elem, last_item
        if data[1] == None:
            full_offset.append(elem)
            last_item = elem

        else:
            for i in full_offset:
                if data[1] == i:
                    start_offset = i[3] + 1
                    end_offset = start_offset + data[0][3]

                    match = (data[0][0], data[0][1], start_offset, end_offset)
                    full_offset.append(match)
                last_item = i


    event_markables = []
    event_tokens = collections.defaultdict(list)

    for elem in root.findall('Markables'):
        new_root = elem.getchildren()
        for child in new_root:

            if child.tag.startswith("EVENT_MENTION"):
                event_id =  child.attrib.get("m_id", "null")
                event_markables.append(event_id)

                for tag in child.findall("token_anchor"):
                    corresponding_token = tag.attrib.get("t_id", "null")
                    event_tokens[event_id].append(corresponding_token)

    sentence_event = collections.defaultdict(list)
    event_sentence = []

#    for sentence, tokens in sentence_token_id.items():
#        for event_id, token in event_tokens.items():
#
#            for i in token:
#                if i in tokens:
#                    sentence_event[event_id].append(i) # event token id per sentence
#                    if sentence not in event_sentence:
#                        event_sentence.append(sentence)

    event_tokens_ = collections.defaultdict(list)
    event_offsets_start = {}
    event_offsets_end = {}

    for event_id, token_list_event in event_tokens.items():
        for elem in full_offset:
            elem_id, elem_token, elem_start_offset, elem_end_offset = elem
            match_token = elem_id + 1
            if str(match_token) in token_list_event:
                event_tokens_[event_id].append(elem_token)

            if token_list_event[0] == str(match_token):
                event_offsets_start[event_id] = elem_start_offset

            if token_list_event[-1] == str(match_token):
                event_offsets_end[event_id] = elem_end_offset

    event_tokens_offsets = collections.defaultdict(list)

    counter = 0
    for event_id, words in event_tokens_.items():
        counter  += 1
        if event_id in event_offsets_start and event_id in event_offsets_end:
            token_val = " ".join(words)
            offsets = (event_offsets_start[event_id], event_offsets_end[event_id],)
            event_tokens_offsets[counter] = (token_val,) + offsets

#    print(event_tokens_offsets)


    for sentence_is, tokens in sentence_tokens.items():
        output = open(outfile1, 'a')
        output.writelines(" ".join(tokens) + "\n")
        output.close()

    for event_id, tokens_offsets in event_tokens_offsets.items():
        output2 = open(outfile2, "a")
        output2.writelines("T" + str(event_id) + "\tEvent " + str(tokens_offsets[1]) + " " + str(tokens_offsets[2]) + "\t" + tokens_offsets[0] + "\n")
        output2.close()


            #
#    counter1 = 0
#    event_list_appo = collections.defaultdict(list)
#
#
#    for k, v in sentence_event.items():
#        for i in v:
#
#            if i in token_string_dict:
#
#                event_out = token_string_dict[i] + "_" + token_offset[i][0] + "_" + token_offset[i][1]
#                event_list_appo[k].append(event_out) # events with offset per sentence
#

#    event_list = collections.defaultdict(list)
#    token_list = collections.defaultdict(list)
#
#    multitoken_event  = {}

#    for k, v in event_list_appo.items():
#        if len(v) == 1:
#            for i in v:
#                event_list[k].append(i)
#        else:
#            start = v[0].split("_")[1]
#            end = v[-1].split("_")[-1]
#            offset_event = start + "_" + end
#            multitoken_event[k] = offset_event
#            for i in range(0, len(v)):
#                val = v[i]
#                val_splitted = val.split("_")
#                token_list[k].append(val_splitted[0])

#    for k, v in multitoken_event.items():
#        if k in token_list:
#            string_offset = "__".join(token_list[k]) + "_" + v
#            event_list[k].append(string_offset)


#    group_per_sentence = collections.defaultdict(list)

#    for k, v in event_list.items():
#        for i in v:
#            group_per_sentence[k[0]].append(i)

#    # same sentence pairs
#    for k, v in group_per_sentence.items():
#        if len(group_per_sentence) > 1:
#            if len(v) > 1:
#                if k in sentence_tokens:
#                    counter1 += 1
##                    print(str(counter1), filename + str(k), " ".join(sentence_tokens[k]), filename + str(k), " ".join(sentence_tokens[k]), "###".join(event_list[k]), "###".join(event_list[k]))
#                    output = open(outfile1, "a")
#                    output.writelines(str(counter1) + "\t" + filename + "_" +  str(k) + "\t" + " ".join(sentence_tokens[k]) + "\t" + filename + "_" + str(k) + "\t" + " ".join(sentence_tokens[k]) + "\t" + "###".join(group_per_sentence[k]) + "\t" + "###".join(group_per_sentence[k]) + "\n")
#                    output.close()



    # different sentence pairs

#    different_sentence_pairs = list(combinations(event_sentence, 2))
#
#    counter2 = counter1
#    for source, target in different_sentence_pairs:
#        counter2 += 1
#        if source in group_per_sentence:
#            if source in sentence_tokens:
#                if target in group_per_sentence:
#                    if source in sentence_tokens:
##                        print(str(counter2), filename +  source,  " ".join(sentence_tokens[source]), filename +target, " ".join(sentence_tokens[target]), "###".join(event_list[source]), "###".join(event_list[target]))
#                        output = open(outfile2, "a")
#                        output.writelines(str(counter2) + "\t" +  filename + "_" + source + "\t" + " ".join(sentence_tokens[source]) + "\t" + filename + "_" + target + "\t" + " ".join(sentence_tokens[target]) + "\t" + "###".join(group_per_sentence[source]) + "\t" + "###".join(group_per_sentence[target]) +"\n")
#                        output.close()


def plot_link_crowd(airbus_dir, outdir):
    for filename in glob.glob(airbus_dir + "/*.xml", recursive=True):

        print(filename)

        outfile1 = outdir + filename.split(".xml")[-0].split("/")[-1] + ".txt"
        outfile2 = outdir + filename.split(".xml")[-0].split("/")[-1] + ".ann"
        get_format_brat(filename, outfile1, outfile2)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python3 data4brat.py [CAT_DATA_DIR] outdir')
    else:
        plot_link_crowd(argv[1], argv[2])

if __name__ == '__main__':
    main()