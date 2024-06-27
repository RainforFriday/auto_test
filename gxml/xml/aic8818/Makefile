#run in hpc02 server
#ssh -X hpc02
#csh
#source setenv
#make gen_pdf

dir = gen

default: gen_html

all: gen_pdf gen_html gen_word

gen_pdf: gen_dir
	@cxmlcvt -i aic8818_hard.xml -dir $(dir) -o pdf  -chipname aic8818_hard -sysname aic8818

gen_html: gen_dir
	@cxmlcvt -i aic8818_hard.xml -dir $(dir) -o html  -chipname aic8818_hard -sysname aic8818 -am 0xFFFF0000

gen_word: gen_dir
	@cxmlcvt -i aic8818_hard.xml -dir $(dir) -o word  -chipname aic8818_hard -sysname aic8818

gen_dir:
	@test -d $(dir) || mkdir $(dir)

clean:
	@rm -rf $(dir)
