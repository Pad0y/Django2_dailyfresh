import jieba
from whoosh.analysis import Tokenizer, Token


class ChineseTokenizer(Tokenizer):
	def __call__(self, value, positions=False, chars=False,
	             keeporiginal=False, removestops=True,
	             start_pos=0, start_char=0, mode='', **kwargs):
		t = Token(positions, chars, removestops=removestops, mode=mode, **kwargs)
		seglist = jieba.cut(value, cut_all=True)
		for w in seglist:
			t.original = t.text = w
			t.boost = 1.0
			if positions:
				t.pos = start_pos + value.find(w)
			if chars:
				t.startchar = start_char + value.find(w)
				t.endchar = start_char + value.find(w) + len(w)
			yield t


def ChineseAnalyzer():
	return ChineseTokenizer()
