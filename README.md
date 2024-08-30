Este projeto é um aplicativo de monitoramento de câmeras com reconhecimento de placas de veículos. Ele usa o YOLOv8 para detecção de objetos e EasyOCR para leitura de texto. A interface é construída com Tkinter e suporta múltiplas câmeras simultaneamente.

Requisitos Mínimos
Python 3.8 ou superior
OpenCV
Pandas
Ultralytics (YOLOv8)
NumPy
EasyOCR
Pillow (PIL)
Tkinter (geralmente incluído com Python)
Dependências
Instale as dependências necessárias usando pip:

Uso
Modelo YOLOv8: Coloque o arquivo best.pt no diretório modelo/.
Classes YOLO: O arquivo coco1.txt deve listar as classes usadas pelo modelo, uma por linha.
Vídeo: Atualize self.rtsp_links com os links das câmeras ou caminhos dos vídeos. No exemplo, há um vídeo de teste (resources/mycarplate.mp4).
Executar: Execute o script. A interface gráfica será aberta e exibirá os feeds das câmeras.
Funcionamento
O aplicativo carrega um modelo YOLOv8 pré-treinado para detecção de objetos e usa EasyOCR para ler placas de veículos.
As placas detectadas e lidas são salvas em um arquivo de log (placas.txt).
Notas
Certifique-se de ter os arquivos e caminhos corretos configurados.
Para melhor desempenho, ajuste o código conforme necessário para o seu ambiente de execução.
Se precisar de mais informações ou ajuda, sinta-se à vontade para perguntar!
