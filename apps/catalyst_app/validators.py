from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime
import re


class RUTValidator:
    """
    Validador para RUT chileno.
    Verifica el formato y calcula el dígito verificador.
    """
    
    @staticmethod
    def clean_rut(rut):
        """
        Limpia el RUT quitando puntos y guion.
        """
        if not rut:
            return None
        rut = str(rut).strip()
        rut = rut.replace('.', '').replace('-', '')
        return rut
    
    @staticmethod
    def calculate_dv(number):
        """
        Calcula el dígito verificador del RUT usando el algoritmo chileno.
        """
        multipliers = [2, 3, 4, 5, 6, 7]
        total = sum(int(digit) * multipliers[i % 6] 
                   for i, digit in enumerate(reversed(number)))
        dv = 11 - (total % 11)
        
        if dv == 11:
            return '0'
        elif dv == 10:
            return 'K'
        else:
            return str(dv)
    
    @staticmethod
    def is_valid_rut(rut):
        """
        Valida un RUT chileno.
        Retorna True si es válido, False en caso contrario.
        """
        if not rut:
            return False
        
        rut = RUTValidator.clean_rut(rut)
        
        # Debe tener al menos 9 caracteres (8 dígitos + 1 verificador)
        if len(rut) < 9:
            return False
        
        # Separar número del dígito verificador
        number_part = rut[:-1]
        dv_part = rut[-1].upper()
        
        # El número debe ser solo dígitos
        if not number_part.isdigit():
            return False
        
        # Calcular el dígito verificador
        calculated_dv = RUTValidator.calculate_dv(number_part)
        
        return dv_part == calculated_dv
    
    def __call__(self, value):
        """
        Llamable para usar como validador en modelos Django.
        """
        if value and not self.is_valid_rut(value):
            raise ValidationError(
                'RUT inválido. Formato correcto: 12345678-9 o 12.345.678-9',
                code='invalid_rut'
            )


class DateValidator:
    """
    Validadores para fechas.
    """
    
    @staticmethod
    def validate_no_future_date(value):
        """
        Valida que la fecha no sea en el futuro.
        """
        today = date.today()
        if isinstance(value, datetime):
            value = value.date()
        
        if value > today:
            raise ValidationError(
                'La fecha no puede ser en el futuro.',
                code='future_date'
            )
    
    @staticmethod
    def validate_end_date_after_start(start_date, end_date):
        """
        Valida que la fecha de término sea posterior a la de inicio.
        """
        if end_date <= start_date:
            raise ValidationError(
                'La fecha de término debe ser posterior a la fecha de inicio.',
                code='invalid_date_range'
            )


class NumericValidator:
    """
    Validadores para campos numéricos.
    """
    
    @staticmethod
    def validate_positive(value):
        """
        Valida que el valor sea positivo.
        """
        if value < 0:
            raise ValidationError(
                'El valor debe ser mayor o igual a 0.',
                code='negative_value'
            )
    
    @staticmethod
    def validate_quantity(value):
        """
        Valida que la cantidad sea un entero positivo.
        """
        if not isinstance(value, int) or value <= 0:
            raise ValidationError(
                'La cantidad debe ser un número entero mayor a 0.',
                code='invalid_quantity'
            )


class TextValidator:
    """
    Validadores para campos de texto.
    """
    
    @staticmethod
    def validate_no_special_chars(value):
        """
        Valida que el texto no contenga caracteres especiales.
        """
        if re.search(r'[<>\"\'%;()&+]', value):
            raise ValidationError(
                'El texto contiene caracteres especiales no permitidos.',
                code='special_chars'
            )
    
    @staticmethod
    def validate_email_format(value):
        """
        Valida que sea un email con formato válido.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValidationError(
                'El formato de email no es válido.',
                code='invalid_email'
            )
    
    @staticmethod
    def validate_phone_format(value):
        """
        Valida que sea un teléfono con formato válido.
        """
        # Acepta +56 9 xxxx xxxx o 9 xxxx xxxx
        pattern = r'^(\+56|0|56)?\s*9?\s*\d{4}\s*\d{4}$'
        cleaned = value.replace('-', '').replace(' ', '')
        if not re.match(pattern, cleaned):
            raise ValidationError(
                'El formato de teléfono no es válido.',
                code='invalid_phone'
            )


# Instancias de validadores para usar en modelos
rut_validator = RUTValidator()
date_validator = DateValidator()
numeric_validator = NumericValidator()
text_validator = TextValidator()
