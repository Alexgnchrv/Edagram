import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                <strong>Python</strong> — высокоуровневый язык программирования, использующийся для создания серверной логики и работы с данными.
              </li>
              <li className={styles.textItem}>
                <strong>Django</strong> — мощный веб-фреймворк для Python, который упрощает разработку веб-приложений и следит за безопасностью и производительностью.
              </li>
              <li className={styles.textItem}>
                <strong>Django REST Framework</strong> — фреймворк для создания API на базе Django, обеспечивающий поддержку RESTful сервисов.
              </li>
              <li className={styles.textItem}>
                <strong>Djoser</strong> — библиотека для упрощения создания аутентификации и авторизации пользователей в Django REST API.
              </li>
              <li className={styles.textItem}>
                <strong>GitHub Actions</strong> — инструмент для автоматизации CI/CD процессов, позволяющий запускать тесты и развертывать код при каждом обновлении репозитория.
              </li>
              <li className={styles.textItem}>
                <strong>Docker</strong> — система контейнеризации, которая позволяет упаковывать приложение с его зависимостями в контейнеры для упрощения развертывания и масштабирования.
              </li>
              <li className={styles.textItem}>
                <strong>asgiref</strong> — библиотека для асинхронных операций в Django, поддерживающая протоколы WebSocket и ASGI.
              </li>
              <li className={styles.textItem}>
                <strong>sqlparse</strong> — библиотека для парсинга SQL-запросов в Django.
              </li>
              <li className={styles.textItem}>
                <strong>django-filter</strong> — инструмент для упрощения добавления фильтрации к данным в Django.
              </li>
              <li className={styles.textItem}>
                <strong>drf-extra-fields</strong> — расширение для Django REST Framework, которое добавляет дополнительные типы полей в API.
              </li>
              <li className={styles.textItem}>
                <strong>Pillow</strong> — библиотека для работы с изображениями в Python, используется для обработки изображений в проекте.
              </li>
              <li className={styles.textItem}>
                <strong>django-cors-headers</strong> — библиотека для разрешения кросс-доменных запросов (CORS) в Django-приложениях.
              </li>
              <li className={styles.textItem}>
                <strong>psycopg2-binary</strong> — драйвер для работы с PostgreSQL в Python, используемый для подключения базы данных к проекту.
              </li>
              <li className={styles.textItem}>
                <strong>python-decouple</strong> — библиотека для управления конфигурациями приложения, позволяющая хранить настройки в отдельных файлах и переменных окружения.
              </li>
              <li className={styles.textItem}>
                <strong>python-dotenv</strong> — инструмент для загрузки настроек из `.env` файлов в переменные окружения.
              </li>
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies
