import pandas as pd

# This regex captures all corporate owners (or business owners) that can be found in deeded_owners
# Note this pattern is designed for Cuyahoga County's dataset and is not tested on other string matching.
biz_flag_re = r"(?i) ?l\.? ?l\.? ?c|\Winco?|\Wcorp|\slp|l-?t-?d|roth ira|limited|\Wtrs\W|-?tru?st?|renovations|liability|resource|enterprise|associ?a?t?|acquisition|comi?pany|\Wco$|llp|\Wl\.?p\.?\W?|management|financial|development|network|invest|co-t|construct|property|properties|solution|buil(der)?|real estate|services|realty|partners?|li?m?i?te?d"

# This captures other special corp names. To be consolidated with main pattern some time.
major_names_re = r"(?i)Sherwin Williams ?C?o?|iplan group|Cleveland Clinic"

# Exclusions we want to explicitly define to make sure they are not considered "corporate"
exclude_re = r"(?i)clev?e?l?a?n?d? elec?|land reutilization|fairfax rennaisance|fairfax homes|university circle,? inc"

def identify_corp_owner(column: pd.Series):
    owner_column = column.copy()
    biz_test = owner_column.str.contains(biz_flag_re)
    major_names_test = owner_column.str.contains(major_names_re)
    exclude_test = owner_column.str.contains(exclude_re).fillna(False)

    final_flags = (biz_test | major_names_test) & ~(exclude_test)
    return final_flags