def user_avatar_upload_to(instance: 'CustomUser', filename: str) -> str:  # noqa: F821 — имя резолвится вызывающим кодом, прямой импорт даст цикл с models
    """
    Сформировать путь загрузки аватара пользователя. users/avatars/<uuid-пользователя>/<файл>

    :param instance: Экземпляр CustomUser.
    :param filename: Исходное имя загружаемого файла.
    :return: Относительный POSIX-путь.
    """

    return f'users/avatars/{instance.pk}/{filename}'
