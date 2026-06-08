import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlIntegrationComponent } from './intl-integration.component';

describe('IntlIntegrationComponent', () => {
  let component: IntlIntegrationComponent;
  let fixture: ComponentFixture<IntlIntegrationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlIntegrationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlIntegrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
