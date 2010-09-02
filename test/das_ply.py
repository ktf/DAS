import ply.lex
import ply.yacc

class DASPLY(object):
    tokens = [
        'PIPE',
        'AGGREGATOR',
        'FILTER',
        'MAPREDUCE',
        'COMMA',
        'LSQUARE',
        'RSQUARE',
        'LPAREN',
        'RPAREN',
        'OPERATOR',
        'OPERATORLIST',
        'WORD',
        'NUMBER',
        'DATE',
        'SPACE'
    ]

    t_PIPE = r'\|'
    t_OPERATOR = r'='
    t_COMMA    = r'\,'
    t_MAPREDUCE = r'NEVER MATCH ME'
    t_LSQUARE = r'\['
    t_RSQUARE = r'\]'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    def t_NUMBER(self, t):
        r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
        t.value = float(t.value)
        return t

    def t_DATE(self, t):
        r'[0-2]0[0-9][0-9][0-1][0-9][0-3][0-9]'
        t.value = int(t.value)
        return t

    def t_WORD(self, t):
        r'''[a-zA-Z/*][a-zA-Z_0-9/*\-#.]+|["'][a-zA-Z_0-9/*\-#. ]+["']'''
        if t.value[0] in ('"',"'") and t.value[-1] in ('"',"'"):
            t.value = t.value[1:-1]
        elif t.value in ('grep', 'unique'):
            t.type = 'FILTER'
        elif t.value == 'last':
            t.type = 'OPERATOR'
        elif t.value in ('in','between'):
            t.type = 'OPERATORLIST'
        elif t.value in ('sum', 'min', 'max', 'avg', 'count'):
            t.type = 'AGGREGATOR'
        return t
    def t_SPACE(self, t):
        r'\ '
        pass

    def p_overall0(self, p):
        '''overall : keys PIPE pipelist'''
        p[0] = {'keys':p[1],'pipe':p[3]}
    def p_overall1(self, p):
        '''overall : keys'''
        p[0] = {'keys':p[1],'pipe':[]}
    def p_pipelist0(self, p):
        '''pipelist : pipelist PIPE pipefunc'''
        p[0] = p[1]+[p[3]]
    def p_pipelist1(self, p):
        '''pipelist : pipefunc'''
        p[0] = [p[1]]
    def p_keyop0(self, p):
        '''keyop : WORD OPERATOR WORD
                 | WORD OPERATOR NUMBER
                 | WORD OPERATOR DATE
                 | WORD OPERATORLIST array'''
        p[0] = ('keyop',p[1],p[2],p[3])
    def p_keys0(self, p):
        '''keys : keys keyop'''
        p[0] = p[1]+[p[2]]
    def p_keys1(self, p):
        '''keys : keyop'''
        p[0] = [p[1]]
    
    def p_array(self, p):
        '''array : LSQUARE list RSQUARE'''
        p[0] = tuple(['array']+p[2])
    def p_list(self, p):
        '''list : list COMMA WORD
                | list COMMA NUMBER
                | list COMMA DATE'''
        p[0] = p[1]+[p[3]]
        
    def p_list2(self, p):
        '''list : WORD
                | NUMBER
                | DATE'''
        p[0] = [p[1]]
    def p_pipefunc0(self, p):
        '''pipefunc : FILTER list'''
        p[0] = tuple(['filter',p[1],p[2]])
    def p_pipefunc1(self, p): #should probably merge this with p_arglist
        '''pipefunc : FILTER'''
        p[0] = tuple(['filter',p[1],None])
    def p_oneagg(self, p):
        '''oneagg : AGGREGATOR LPAREN WORD RPAREN'''
        p[0] = tuple(['aggregator',p[1],p[3]])
    def p_agglist0(self, p):
        '''agglist : agglist COMMA oneagg'''
        p[0] = p[1]+[p[3]]
    def p_agglist1(self, p):
        '''agglist : oneagg'''
        p[0] = [p[1]]
    def p_pipefunc2(self, p):
        '''pipefunc : agglist'''
        p[0] = tuple(['aggregators']+p[1])
    def p_keyop1(self, p):
        '''keyop : WORD'''
        p[0] = ('keyop',p[1],None,None)
        
    def build(self,**kwargs):
        self.lexer = ply.lex.lex(module=self, **kwargs)
        self.parser = ply.yacc.yacc(module=self, **kwargs)
        
if __name__=='__main__':
    p = DASPLY()
    p.build()
    queries = [
    "dataset file=/abc/def epoch in [123,456] | grep file.name, file.age | unique | sum(file.size),max(file.size)",
    "site=T1_CH_CERN",
    "monitor",
    "jobsummary",
    "primary_ds",
    "block=/Wgamma/Winter09_IDEAL_V12_FastSim_v1/GEN-SIM-DIGI-RECO#9f5c396b-b6a1-4efc-aaca-d2193ff1c341",
    "dataset=/Wgamma/Winter09_IDEAL_V12_FastSim_v1/GEN-SIM-DIGI-RECO",
    "block dataset=/Wgamma/Winter09_IDEAL_V12_FastSim_v1/GEN-SIM-DIGI-RECO",
    "file dataset=/Wgamma/Winter09_IDEAL_V12_FastSim_v1/GEN-SIM-DIGI-RECO | grep file.name, file.size",
    "block dataset=/QCDpt30/Summer08_IDEAL_V9_skim_hlt_v1/USER",
    "file dataset=/QCDpt30/Summer08_IDEAL_V9_skim_hlt_v1/USER | grep file.name, file.size",
    "config dataset=/Wgamma/Winter09_IDEAL_V12_FastSim_v1/GEN-SIM-DIGI-RECO",
    "file=/store/mc/Winter09/Wgamma/GEN-SIM-DIGI-RECO/IDEAL_V12_FastSim_v1/0000/06C82617-4A15-DE11-B068-0014C23ADC8E.root",
    "run=20853",
    "run in [20853,20859]",
    "release=CMSSW_2_0_8",

    "latitude=42 longitude=-77",
    "zip=14850",
    "city=Ithaca",
    "ip=137.138.141.145 | grep ip.City",
    "dataset | grep dataset.name",
    ]
    for query in queries:
        print
        print query
        print p.parser.parse(query)