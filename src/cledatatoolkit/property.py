
# This regex captures all corporate owners (or business owners) that can be found in deeded_owners
# Note this pattern is designed for Cuyahoga County's dataset and is not tested on other string matching.
biz_flag_regex = r"(?i) ?l\.? ?l\.? ?c|\Winco?|\Wcorp|\slp|l-?t-?d|roth ira|limited|\Wtrs\W|-?tru?st?|renovations|liability|resource|enterprise|associ?a?t?|acquisition|comi?pany|\Wco$|llp|\Wl\.?p\.?\W?|management|financial|development|network|invest|co-t|construct|property|properties|solution|buil(der)?|real estate|services|realty|partners?|li?m?i?te?d"
