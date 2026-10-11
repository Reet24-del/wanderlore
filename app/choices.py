"""Bounded fictional decisions: never walking directions or physical tasks."""
def for_chapter(canon, chapter):
    obj=canon['object']; companion=canon['companion']
    return [
        {'id':f'{chapter}:examine','label':f'Look for a hidden detail in the {obj}', 'consequence':f'In the fiction, examining the {obj} reveals a tiny engraved symbol. Use that symbol as the next clue.'},
        {'id':f'{chapter}:ask','label':f'Ask {companion} what they remember', 'consequence':f'{companion} recalls a promise made to an old friend. That memory reveals the next clue.'},
        {'id':f'{chapter}:trust','label':'Offer to help before asking for answers', 'consequence':f'The walker offers help freely. {companion} responds to this kindness by revealing a secret about the {obj}.'},
    ]
