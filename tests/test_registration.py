import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

# Возможные варианты тестов:
"""
Тест добавления пользователя с существующим логином.
Тест успешной аутентификации пользователя.
Тест аутентификации несуществующего пользователя.
Тест аутентификации пользователя с неправильным паролем.
Тест отображения списка пользователей.
"""

def test_add_duplicate_username(setup_database, connection):
    """Тест попытки добавления пользователя с уже существующим логином."""
    # Добавляем первого пользователя
    add_user('duplicateuser', 'dup@example.com', 'pass123')

    # Пытаемся добавить пользователя с тем же логином
    added = add_user('duplicateuser', 'another@email.com', 'newpass')
    assert added is False, "Не должно быть возможно добавить пользователя с дублирующимся логином."

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='duplicateuser'")
    count = cursor.fetchone()[0]
    assert count == 1, "Должен существовать только один пользователь с таким логином."


def test_successful_authentication(setup_database):
    """Тест успешной аутентификации пользователя."""
    add_user('authuser', 'auth@example.com', 'correctpass')
    authenticated = authenticate_user('authuser', 'correctpass')
    assert authenticated is True, "Авторизация должна быть успешной."


def test_authenticate_nonexistent_user(setup_database):
    """Тест аутентификации несуществующего пользователя."""
    authenticated = authenticate_user('nonexistent', 'any_password')
    assert authenticated is False, "Несуществующий пользователь не должен пройти аутентификацию."

def test_authenticate_wrong_password(setup_database):
    """Тест аутентификации с неверным паролем."""
    add_user('wrongpassuser', 'wrongpass@example.com', 'rightpassword')
    authenticated = authenticate_user('wrongpassuser', 'wrongpassword')
    assert authenticated is False, "Аутентификация должна провалиться при неверном пароле."


def test_display_users(capfd, setup_database):
    """Тест вывода списка пользователей."""
    add_user('user1', 'user1@example.com', 'pass1')
    add_user('user2', 'user2@example.com', 'pass2')

    display_users()

    captured = capfd.readouterr()
    assert "Логин: user1" in captured.out
    assert "Электронная почта: user1@example.com" in captured.out
    assert "Логин: user2" in captured.out
    assert "Электронная почта: user2@example.com" in captured.out