# pievdcs
Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais

* O presente projeto tem como objetivo o desenvolvimento de uma plataforma digital no modelo SaaS (Software as a Service), voltada ao enfrentamento da violência doméstica e crimes sexuais. A plataforma integrará as forças de segurança pública, núcleos municipais de atenção à família, Ministério Público, Defensoria Pública e o Poder Judiciário. A atividade central é a criação de um sistema seguro, colaborativo e funcional, que permita o compartilhamento de informações, acompanhamento de casos e articulação de ações interinstitucionais, proporcionando mais agilidade e efetividade no atendimento às vítimas.

* O projeto será desenvolvido por um reeducando com formação técnica, que terá a oportunidade de aplicar, na prática, os conhecimentos adquiridos sob supervisão institucional. Essa iniciativa reforça o papel do sistema prisional como agente de transformação social, ao oferecer condições reais para a ressocialização por meio do trabalho qualificado. Além de gerar impacto social direto, a ação contribui para a valorização profissional do reeducando e demonstra à sociedade que a reinserção de pessoas privadas de liberdade é possível e benéfica. A priorização do uso de tecnologias assertivas e de código aberto garante que a plataforma seja sustentável, escalável e viável a longo prazo. O projeto contempla os Eixos 1 e 2 do edital.

____________________

##### [Requisitos Não Funcionais]
* 01: Alta segurança da informação (criptografia, controle de acesso, autenticação forte).
* 02: Usabilidade elevada, com foco na experiência de pessoas em situação de vulnerabilidade.
* 03: Alta disponibilidade e estabilidade do sistema.
* 04: Compatibilidade com dispositivos móveis e diferentes navegadores.
* 05: Escalabilidade para atender um número crescente de instituições.
* 06: Baixo custo de manutenção, utilizando tecnologias de código aberto.
* 07: Interface intuitiva e acessível, seguindo diretrizes de acessibilidade digital.
* 08: Desempenho adequado mesmo em redes móveis com baixa qualidade.
* 09: Conformidade com a LGPD (Lei Geral de Proteção de Dados).

##### [Requisitos Funcionais]
* 01: Cadastro de casos de violência doméstica e crimes sexuais.
* 02: Acompanhamento do status dos casos em tempo real por instituições parceiras.
* 03: Compartilhamento seguro de dados entre diferentes instituições (segurança, MP, Judiciário etc.).
* 04: Interface de chatbot para acolhimento e orientação inicial às vítimas.
* 05: Cadastro e autenticação de usuários com diferentes níveis de acesso.
* 06: Dashboard com indicadores e estatísticas para tomada de decisão.
* 07: Sistema de notificações e alertas para ações pendentes ou emergenciais.
* 08: Integração com sistemas existentes de instituições públicas.
* 09: Módulo para capacitação de operadores e representantes.
* 10: Suporte a múltiplos dispositivos, incluindo tablets e smartphones.




<h3>Pertinentes as informações do BANCO DE DADOS.</h3>
(FK) = Chave Estrangeira
(PK) = Chave Primaria
(MPU) = Medida Protetiva de Urgência

<li>Vítima:</li>
<p>&#x2610; ID vítima : INT --- AUTO_INCREMENT.</p>
<p>&#x2610; Nome da vítima : str[250].</p>
<p>&#x2610; CPF : int[11] --- PK.</p>
<p>&#x2610; data de nascimento : Date.</p>
<p>&#x2610; Idade : int[3].</p>
<p>&#x2610; Contato telefonico : int[15].</p>
<p>&#x2610; n° AUTOS : int[150]. --- FK da 'violência domestica'</p>
<p>&#x2610; Nome do Agressor : int[150]. --- FK do 'Agressor'</p>
<p>&#x2610; Idade : int[3].</p>
<p>&#x2610; Início dos AUTOS : Date.</p>
<p>&#x2610; Status : Bool --- Dropbox .</p>
<p>&#x2610; Date última visita : Date --- FK da 'PM atendimento'.</p>
<p>&#x2610; Idade : int[3].</p>
<p>&#x2610; Municipio : str[15] --- Dropbox.</p>
<p>&#x2610; Bairro : str[15] --- Dropbox.</p>
<p>&#x2610; Rua : str[100].</p>
<p>&#x2610; Numero da residencia : int[5].</p>





<li>Agressor:</li>
<p>&#x2610; ID Agressor : INT --- AUTO_INCREMENT.</p>
<p>&#x2610; Nome do Agressor : int[150].</p>
<p>&#x2610; CPF : int[11] --- PK.</p>
<p>&#x2610; data de nascimento : Date.</p>
<p>&#x2610; Idade : int[3].</p>
<p>&#x2610; Contato telefonico : int[15].</p>
<p>&#x2610; n° AUTOS : int[150]. --- chave extrangeira da 'violência domestica'</p>
<p>&#x2610; Nome da vítima : int[150]. --- chave extrangeira da 'vítima'</p>
<p>&#x2610; Idade : int[3].</p>
<p>&#x2610; Início dos AUTOS : Date.</p>
<p>&#x2610; Status : Bool --- Dropbox .</p>
<p>&#x2610; Date última visita : Date --- chave extrangeira da 'PM atendimento'.</p>
<p>&#x2610; Idade : int[3].</p>
<p>&#x2610; Municipio : str[15] --- Dropbox.</p>
<p>&#x2610; Bairro : str[15] --- Dropbox.</p>
<p>&#x2610; Rua : str[100].</p>
<p>&#x2610; Numero da residencia : int[5].</p>



<li>Violência domestica:</li>
<p>&#x2610; n° AUTOS : int[150].</p>
<p>&#x2610; Tipo da agressão : str[50] --- Dropbox.</p>
<p>&#x2610; Grau de Parentesco : str[50] --- Dropbox.</p>
<p>&#x2610; MPU : str[50] --- Dropbox.</p>



<li>Ususario:</li>
<p>&#x2610; xxxxxxx.</p>
<p>&#x2610; XXXXXXXXX.</p>