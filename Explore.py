import matplotlib.pyplot as plt
import pandas as pd
import re
import seaborn as sns

sns.set_theme("paper")
sns.color_palette()

enne = pd.read_csv("Data\Enneagram_Full.csv", names=["user", "flair"])
mbti = pd.read_csv("Data\mbti_Full.csv", names=["user", "flair"])

mbti_order = [
    "INTJ",
    "INTP",
    "ENTJ",
    "ENTP",
    "INFJ",
    "INFP",
    "ENFJ",
    "ENFP",
    "ISTJ",
    "ISFJ",
    "ESTJ",
    "ESFJ",
    "ISTP",
    "ISFP",
    "ESTP",
    "ESFP",
]
enne_order = [
    "5w4",
    "5",
    "5w6",
    "6w5",
    "6",
    "6w7",
    "7w6",
    "7",
    "7w8",
    "8w7",
    "8",
    "8w9",
    "9w8",
    "9",
    "9w1",
    "1w9",
    "1",
    "1w2",
    "2w1",
    "2",
    "2w3",
    "3w2",
    "3",
    "3w4",
    "4w3",
    "4",
    "4w5",
]

mbti_replace = {
    "[INTJ]": "INTJ",
    "[INTP]": "INTP",
    "[ENTJ]": "ENTJ",
    "[INFP]": "INFP",
    "[ENFP Queen] [EIE] [4w5] 8==D": "ENFP",
    "[INTP]": "INTP",
    "[INTP] 9w1": "INTP",
    "[INFP] 4w3": "INFP",
    "[INFJ]": "INFJ",
    "[ENTP]": "ENTP",
    "INFP: Breathe in strength, breathe out bullshit.": "INFP",
    "[ESTJ] 6w5": "ESTJ",
    "[INTJ] 1w2": "INTJ",
    "ENFJ 4w5": "ENFJ",
    "[ESTP]": "ESTP",
    "enfp 9- all my own stunts": "ENFP",
    "☺INFP☺4w5": "INFP",
    "[ENFJ]": "ENFJ",
    "[INTP] ": "INTP",
}
enne_in_mbti = [
    "[ENFP Queen] [EIE] [4w5] 8==D",
    "[INTP] 9w1",
    "[INFP] 4w3",
    "[ESTJ] 6w5",
    "[INTJ] 1w2",
    "ENFJ 4w5",
    "enfp 9- all my own stunts",
    "☺INFP☺4w5",
]
enne_replace = {
    "~ E N T P  5 w 4 ~": "5w4",
    "INTP 5+4": "5w4",
    "4wTHREE HEE sp/so": "4w3",
    "4sx INTJ": "4",
    "ENTP 5wX sx": "5",
    "6sp w 5": "6w5",
    "INTP ~9?": "9",
    "9w? ISTP": "9",
    "INTP 5w?": "5",
    "9(45)w8 so/sp": "9w8",
    "(4)51 sx/sp INTJ": "4",
    "INTP 5": "5",
    "ENTP - type 3": "3",
    "6": "6",
    "SP3": "3",
    "Infj 8": "8",
    "Sx 4": "4",
}

enne_exclude = [
    "749 Not necessarily in this order",
    "546738 hexatype",
    "9-4-6",
    "2,7,or 9?",
    "4w8",
    "INFJ Sp/So",
    "6-9-2",
    "idk",
    "8 5 4 sx/so NeTi",
    "4, 9 or 7?? im still confused|INFP",
    "5-8-4 INTJ so/sx",
    "5-8-4 INTJ so/sx",
    "ENTP \\\\ type me",
    "8w1",
    "unsure",
    "???",
    "?????",
    "5w1",
    "5w7",
    "ENTP, not sure what enneagram.",
    "x31 sp/so",
    "9/2",
    "4 or 5 idk",
    "No god damn clue!",
    "Somewhere in Shame",
    "not sure yet",
    "INFx 4/6w? (so/sp)",
    "5 - 2 - 1 sx/sp",
]
mbti_exclude = ["[INFx]"]

overlap = enne.merge(mbti, on="user").drop_duplicates("user")
overlap = overlap[
    overlap["flair_x"].apply(lambda x: isinstance(x, str))
    & overlap["flair_y"].apply(lambda y: isinstance(y, str))
]

overlap.loc[
    overlap["flair_x"].apply(lambda x: re.search(r"[1-9]w[1-9]", x) is not None),
    "flair_x",
] = overlap[
    overlap["flair_x"].apply(lambda x: re.search(r"[1-9]w[1-9]", x) is not None)
][
    "flair_x"
].apply(
    lambda x: re.search(r"[1-9]w[1-9]", x).group(0)
)

overlap.loc[
    overlap["flair_x"].apply(lambda x: re.search(r"[1-9] ", x) is not None), "flair_x"
] = overlap[overlap["flair_x"].apply(lambda x: re.search(r"[1-9] ", x) is not None)][
    "flair_x"
].apply(
    lambda x: re.search(r"[1-9] ", x).group(0)[:-1]
)

overlap.loc[
    overlap["flair_x"].apply(lambda x: re.search(r"[1-9],", x) is not None), "flair_x"
] = overlap[overlap["flair_x"].apply(lambda x: re.search(r"[1-9],", x) is not None)][
    "flair_x"
].apply(
    lambda x: re.search(r"[1-9],", x).group(0)[:-1]
)

overlap["flair_x"].replace(enne_replace, inplace=True)
overlap["flair_y"].replace(mbti_replace, inplace=True)
for i in overlap[overlap["flair_x"].isin(enne_exclude)].index:
    overlap.drop(i, inplace=True)
for i in overlap.loc[
    overlap["flair_x"].apply(lambda x: re.search(r"[1-9]{3}", x) is not None)
].index:
    overlap.drop(i, inplace=True)  # drop trigrams or w/e they called
for i in overlap[overlap["flair_y"].isin(mbti_exclude)].index:
    overlap.drop(i, inplace=True)

ct = pd.crosstab(overlap["flair_x"], overlap["flair_y"])
ct = ct[mbti_order]
ct = ct.reindex(enne_order)

plt, ax = plt.subplots(
    2, 2, gridspec_kw={"width_ratios": [4, 1], "height_ratios": [1, 4]}
)
plt.suptitle("Users with flair set on r/mbti and r/Enneagram", y=0.95, fontsize=14)
sns.heatmap(
    ct,
    annot=ct.applymap(lambda x: x if x >= 10 else ""),
    fmt="",
    ax=ax[1][0],
    cbar=False,
)
ax[1][0].set_yticks([x + 0.5 for x in list(range(27))])
ax[1][0].set_yticklabels(enne_order)
ax[1][0].set_ylabel("Enneagram")
ax[1][0].set_xlabel("MBTI")
ax[0][1].remove()
mbti_counts = overlap["flair_y"].value_counts().reindex(mbti_order)
sns.barplot(x=mbti_counts.index, y=mbti_counts, ax=ax[0][0])
ax[0][0].set_ylabel("")
enne_counts = overlap["flair_x"].value_counts().reindex(enne_order)
sns.barplot(x=enne_counts, y=enne_counts.index, ax=ax[1][1])
ax[1][1].set_xlabel("")
plt.show()
