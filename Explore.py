import matplotlib.pyplot as plt
import matplotlib.patches
import pandas as pd
from Personalities import (
    mbti_order,
    type_to_name,
    enne_order,
    mbti_replace,
    enne_replace,
    enne_exclude,
    mbti_exclude,
)
import re
import seaborn as sns

sns.set_theme("paper")
sns.color_palette()

enne = pd.read_csv("Data\Enneagram_Full.csv", names=["user", "flair"])
mbti = pd.read_csv("Data\mbti_Full.csv", names=["user", "flair"])

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

fig, ax = plt.subplots(
    2, 2, gridspec_kw={"width_ratios": [4, 1], "height_ratios": [1, 4]}
)
fig.suptitle("Users with flair set on r/mbti and r/Enneagram", y=0.95, fontsize=14)
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

sns.set_theme("notebook")
ax = plt.subplot(2, 1, 1)
mbti_base = mbti.value_counts("flair").head(16)
mbti_base = mbti_base.reindex(mbti_order)
sns.barplot(x=mbti_base.index, y=mbti_base / sum(mbti_base), ax=ax)
plt.title("Users with flair on r/mbti")
plt.xlabel("")
plt.suptitle("Users with flair set on r/mbti and r/Enneagram", y=0.95, fontsize=14)
ax = plt.subplot(2, 1, 2)
sns.barplot(x=mbti_counts.index, y=mbti_counts / sum(mbti_counts), ax=ax)
plt.title("Users with flair on both subreddits")
plt.ylabel("")
plt.show()
mbti_base_proc = pd.DataFrame(
    mbti_base / sum(mbti_base), columns=["% users with flair"]
)
mbti_base_proc["Type"] = "Just r/mbti"
mbti_counts_proc = pd.DataFrame(
    (mbti_counts / sum(mbti_counts)).values,
    index=mbti_counts.index,
    columns=["% users with flair"],
)
mbti_counts_proc["Type"] = "r/mbti and r/Enneagram"
mbti_comb = pd.concat([mbti_base_proc, mbti_counts_proc])
ax = sns.barplot(
    x=mbti_comb["% users with flair"],
    y=mbti_comb.index,
    hue=mbti_comb["Type"],
    palette="hls",
)
ax.xaxis.set_major_formatter(lambda x, y: f"{x*100:.1f} %")
plt.suptitle("Distribution of users with flair set on r/mbti", y=0.95, fontsize=14)
plt.show()

enne_base = enne.value_counts("flair").head(27)
enne_base = enne_base.reindex(enne_order)
enne_base_proc = pd.DataFrame(
    (enne_base / sum(enne_base)).values,
    index=enne_base.index,
    columns=["% users with flair"],
)
enne_base_proc["Type"] = "Juse r/Enneagram"
enne_counts_proc = pd.DataFrame(
    (enne_counts / sum(enne_counts)).values,
    index=enne_counts.index,
    columns=["% users with flair"],
)
enne_counts_proc["Type"] = "r/mbti and r/Enneagram"
enne_comb = pd.concat([enne_base_proc, enne_counts_proc])

ax = sns.barplot(
    y=enne_comb["% users with flair"], x=enne_comb.index, hue=enne_comb["Type"]
)
ax.yaxis.set_major_formatter(lambda x, y: f"{x*100:.1f} %")
plt.suptitle("Distribution of users with flair set on r/Enneagram", y=0.95, fontsize=14)
plt.show()

ax = sns.barplot(
    x=enne_comb["% users with flair"],
    y=enne_comb.index,
    hue=enne_comb["Type"],
    palette="hls",
)
ax.xaxis.set_major_formatter(lambda x, y: f"{x*100:.1f} %")
plt.suptitle("Distribution of users with flair set on r/Enneagram", y=0.95, fontsize=14)
plt.show()

# shout out to jsgounot
def change_height(ax, new_value):
    for patch in ax.patches:
        if a := patch.get_alpha():
            nv = 1
            patch.set_linewidth(0)
            # c = patch.get_color()
            # patch.set_edgecolor(c)
        else:
            nv = new_value
        current_height = patch.get_height()
        diff = current_height - nv
        patch.set_height(nv)
        patch.set_y(patch.get_y() + diff * 0.5)


diff = enne_base_proc["% users with flair"] - enne_counts_proc["% users with flair"]
ax = sns.barplot(x=diff, y=enne_counts_proc.index)
for patch in ax.patches:
    if patch.get_width() < 0:
        patch.set_color("#ff796c")
    else:
        patch.set_color("#75bbfd")
    patch.set_alpha(0.15)
    patch.set_x(-1)
    patch.set_width(2)
ax = sns.barplot(
    x=enne_base_proc["% users with flair"], y=enne_base_proc.index, color="#75bbfd"
)
ax = sns.barplot(
    x=enne_counts_proc["% users with flair"] * -1,
    y=enne_counts_proc.index,
    color="#ff796c",
)
change_height(ax, 0.5)
diff = enne_base_proc["% users with flair"] - enne_counts_proc["% users with flair"]
ax = sns.barplot(x=diff, y=enne_counts_proc.index, color="#53fca1")
ax.xaxis.set_major_formatter(lambda x, y: f"{abs(x*100):.0f} %")
for patch in ax.patches:
    if patch.get_height() == 0.8:
        width = patch.get_width()
        y = patch.get_y() + 0.6
        if width > 0:
            x = patch.get_x() + width
            # t.set_bbox(dict(facecolor="#75bbfd", alpha=0.5, edgecolor="#75bbfd"))
        else:
            x = 0
            # t.set_bbox(dict(facecolor="#ff796c", alpha=0.5, edgecolor="#ff796c"))
        # plt.text(.12, -.8, "Difference", font="Arial", fontsize=11)
        t = ax.text(0.137, y, f"{(width*100):.1f} %", fontsize=11)
plt.legend(
    [
        matplotlib.patches.Patch(color="#ff796c"),
        matplotlib.patches.Patch(color="#75bbfd"),
        matplotlib.patches.Patch(color="#53fca1"),
    ],
    ["Flair set on both subreddits", "Flair set on Enneagram", "Difference"],
    loc=0,
)
plt.title("Distribution of users with flair set on r/Enneagram", fontsize=16)
ax.grid(False)
plt.show()
