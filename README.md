# where Mentor comes from 
It's long been steep and overwhelming for self-learning, as either nobody guides us nor watches us or too many tips flooding in the Internet that we become hesitated to choose and carry out plans. 
Thus, Mentor is created to offer self-learners as well as all other learners a personal mentor, who structures information to present you with an explicit intuitive map that serves as a manual to reach your goals. 
# what Mentor will do
Currently it only show prerequistes based on user query.
In the future, we wish integrating digital-human (live2D) into Mentor 
# what problems we meet and our solutions 
Q: how to display knowledge relationship 
A: applying graph theory, using nodes to represent knowledges and edges to show relationship 
Q: how to store relationship/notes pairs
A: referring existing graph databases 
# how Mentor work 
## graph database
1. get query from user
2. search in database to match query
3. put results in the user-defined form (project-graph compatible markdown)
# project log and plan
- [x] build MVP ( minimum viable product ): a flet app that has basic functions :: frontend contributed by tuhangming and searching module by chenyanxuan
- graph database
	- User-defined searching algorithm and configuration
		- [ ] Vespa search engine
			- [x] native BM25
		- [ ] free depth search: choosing different algorithm for different searching depth
	- AI harness 
		- [ ] able to use llm api, get llm outputs
		- [ ] mcp-server
		- [ ] cli
	- Diverse output form
		- [ ] Mermaid
	- Multiple database form
		- [x] JSON
		- [ ] Mermaid
		- [ ] Markdown
		- [ ] Yaml (dent/tab)
		- [ ] Natural language
	- Data structure
		- [ ] Weights of prerequisites
		- [ ] Distinguish between goals and methods
	- Data converter