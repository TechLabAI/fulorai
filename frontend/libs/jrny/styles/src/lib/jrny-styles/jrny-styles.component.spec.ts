import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyStylesComponent } from './jrny-styles.component';

describe('JrnyStylesComponent', () => {
  let component: JrnyStylesComponent;
  let fixture: ComponentFixture<JrnyStylesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyStylesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyStylesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
